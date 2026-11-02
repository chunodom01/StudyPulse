import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8001",
});

export const getSessions = () => api.get("/sessions/");
export const createSession = (data) => api.post("/sessions/", data);
export const updateSession = (id, data) => api.put(`/sessions/${id}`, data);
export const deleteSession = (id) => api.delete(`/sessions/${id}`);
export const getTip = (lang = "en") => api.get("/ai/tip", { params: { lang } });