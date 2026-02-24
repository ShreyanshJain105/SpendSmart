import client from "./client";

export const getBudgets = (params = {}) => client.get("/budgets", { params });
export const createBudget = (data) => client.post("/budgets", data);
export const updateBudget = (id, data) => client.put(`/budgets/${id}`, data);
export const deleteBudget = (id) => client.delete(`/budgets/${id}`);
