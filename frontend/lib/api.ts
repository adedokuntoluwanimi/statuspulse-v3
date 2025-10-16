import axios from "axios";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window === "undefined"
    ? "http://backend:8000"
    : "http://localhost:8081");

export async function getSites() {
  const { data } = await axios.get(`${API_BASE}/sites`);
  return data;
}

export async function addSite(url: string) {
  const { data } = await axios.post(`${API_BASE}/sites`, { url });
  return data;
}

export async function getStatus(id: number) {
  const { data } = await axios.get(`${API_BASE}/status/${id}`);
  return data;
}

export async function getHistory(id: number) {
  const { data } = await axios.get(`${API_BASE}/history/${id}`);
  return data;
}

