import axios from "axios";

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });

export const runLDA = (texts, n_topics, n_top_words) =>
  api.post("/api/v1/lda", { texts, n_topics, n_top_words });

export const runNMF = (texts, n_topics, n_top_words) =>
  api.post("/api/v1/nmf", { texts, n_topics, n_top_words });

export const runCluster = (texts, n_clusters) =>
  api.post("/api/v1/cluster", { texts, n_clusters });
