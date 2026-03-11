import cv2
import numpy as np
import tensorflow as tf


def _is_conv_like(layer):
    return isinstance(
        layer,
        (
            tf.keras.layers.Conv2D,
            tf.keras.layers.DepthwiseConv2D,
            tf.keras.layers.SeparableConv2D,
        ),
    )


def find_last_conv_layer_name(model, preferred_names=None):
    preferred_names = preferred_names or ("Conv_1",)
    for name in preferred_names:
        try:
            layer = model.get_layer(name)
            if getattr(layer.output.shape, "rank", None) == 4 and _is_conv_like(layer):
                return name
        except Exception:
            continue

    # Prefer the deepest conv-like 4D layer.
    for layer in reversed(model.layers):
        try:
            if layer.output.shape.rank == 4 and _is_conv_like(layer):
                return layer.name
        except Exception:
            continue

    # Final fallback: any 4D feature map.
    for layer in reversed(model.layers):
        try:
            if layer.output.shape.rank == 4:
                return layer.name
        except Exception:
            continue
    raise ValueError("No suitable convolutional layer found for Grad-CAM")


def make_gradcam_heatmap(img_array, model, pred_index=None, preferred_layer_names=None):
    layer_name = find_last_conv_layer_name(model, preferred_names=preferred_layer_names)
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(layer_name).output, model.output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, preds = grad_model(img_array)
        if isinstance(preds, (list, tuple)):
            preds = preds[0]

        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        if preds.shape[-1] == 1:
            class_channel = preds[:, 0]
        else:
            class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    if grads is None:
        raise ValueError("Failed to compute Grad-CAM gradients")

    # Guided Grad-CAM improves localization stability for noisy medical scans.
    guided_mask = tf.cast(conv_outputs > 0, "float32") * tf.cast(grads > 0, "float32")
    guided_grads = guided_mask * grads

    weights = tf.reduce_mean(guided_grads, axis=(1, 2))
    conv_outputs = conv_outputs[0]
    weights = weights[0]
    heatmap = tf.reduce_sum(conv_outputs * weights[tf.newaxis, tf.newaxis, :], axis=-1)
    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.reduce_max(heatmap)
    if float(max_val) <= 1e-10:
        raise ValueError("Degenerate Grad-CAM map")
    heatmap = heatmap / (max_val + 1e-8)
    return heatmap.numpy().astype(np.float32)


def overlay_heatmap_on_image(original_path, heatmap, output_path, alpha=0.5):
    original = cv2.imread(original_path)
    if original is None:
        raise ValueError("Invalid image for Grad-CAM overlay")

    h, w = original.shape[:2]
    heatmap = cv2.resize(heatmap, (w, h))
    heatmap = np.clip(heatmap, 0.0, 1.0)
    heatmap = cv2.GaussianBlur(heatmap, (0, 0), sigmaX=1.5, sigmaY=1.5)

    heatmap_u8 = np.uint8(255 * heatmap)
    heatmap_color = cv2.applyColorMap(heatmap_u8, cv2.COLORMAP_TURBO)
    blended = cv2.addWeighted(original, 1.0 - alpha, heatmap_color, alpha, 0)

    # Keep overlay mostly on high-activation zones to avoid full-image tinting.
    threshold = np.percentile(heatmap, 65)
    mask = (heatmap >= threshold).astype(np.float32)[..., None]
    overlay = np.uint8((1.0 - mask) * original + mask * blended)
    cv2.imwrite(output_path, overlay)


def generate_gradcam_overlay(
    image_path,
    model,
    class_index,
    output_path,
    image_size=224,
    last_conv_layer_name="Conv_1",
):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Invalid image for Grad-CAM")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (image_size, image_size)).astype("float32") / 255.0
    img_array = np.expand_dims(image, axis=0)

    preferred_layers = (
        "Conv_1",
        "block_16_project",
        "block_16_depthwise",
        "out_relu",
        last_conv_layer_name,
    )
    heatmap = make_gradcam_heatmap(
        img_array,
        model,
        pred_index=class_index,
        preferred_layer_names=preferred_layers,
    )
    overlay_heatmap_on_image(image_path, heatmap, output_path)


def generate_fallback_overlay(image_path, output_path, alpha=0.45):
    """
    Always-available fallback heatmap when Grad-CAM cannot be computed.
    Uses image gradient magnitude as a proxy attention map.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Invalid image for fallback overlay")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = cv2.magnitude(gx, gy)
    mag = cv2.GaussianBlur(mag, (0, 0), sigmaX=2.0, sigmaY=2.0)

    max_val = float(np.max(mag))
    if max_val <= 1e-8:
        mag = np.zeros_like(gray, dtype=np.uint8)
    else:
        mag = np.uint8(255 * (mag / max_val))

    heatmap = cv2.applyColorMap(mag, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(image, 1.0 - alpha, heatmap, alpha, 0)
    cv2.imwrite(output_path, overlay)
