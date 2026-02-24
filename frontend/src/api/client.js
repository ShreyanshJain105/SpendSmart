/**
 * Axios base client.
 *
 * All API calls go through this instance, so:
 * - The base URL is configured in exactly one place.
 * - Error normalisation happens once — callers always receive the same shape.
 */
import axios from "axios";

const client = axios.create({
    baseURL: "http://localhost:5000/api",
    headers: { "Content-Type": "application/json" },
    timeout: 10_000,
});

/**
 * Response interceptor: unwrap `.data` on success, normalise errors so UI
 * code never has to dig into Axios internals.
 */
client.interceptors.response.use(
    (res) => res.data,
    (err) => {
        const message =
            err.response?.data?.error ??
            err.message ??
            "An unexpected error occurred";
        return Promise.reject(new Error(message));
    }
);

export default client;
