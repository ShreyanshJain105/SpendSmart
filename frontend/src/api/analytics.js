import client from "./client";

export const getSummary = (month) =>
    client.get("/analytics/summary", { params: { month } });

export const getBreakdown = (month) =>
    client.get("/analytics/breakdown", { params: { month } });

export const getTrends = (months = 6) =>
    client.get("/analytics/trends", { params: { months } });

export const categorizeDescription = (description) =>
    client.post("/ai/categorize", { description });
