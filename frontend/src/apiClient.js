import axios from "axios";
import API_BASE_URL from "./api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export function getApiError(err, fallback = "Request failed") {
  return err?.response?.data?.error || err?.message || fallback;
}

export default apiClient;
