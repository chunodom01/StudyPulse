import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8001",
});

export const getSessions = () => api.get("/sessions/");
export const createSession = (data) => api.post("/sessions/", data);
export const getTip = () => api.get("/ai/tip");