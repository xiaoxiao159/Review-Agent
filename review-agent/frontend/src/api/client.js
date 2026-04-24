import axios from "axios";
const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const ACCESS_KEY = "review_agent_access_token";
const REFRESH_KEY = "review_agent_refresh_token";
const client = axios.create({ baseURL, timeout: 15000 });
let isRefreshing = false;
function getAccessToken() {
    return localStorage.getItem(ACCESS_KEY) || "";
}
function getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY) || "";
}
function setTokens(tokens) {
    localStorage.setItem(ACCESS_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}
export function clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
}
client.interceptors.request.use((config) => {
    const access = getAccessToken();
    if (access) {
        config.headers = config.headers || {};
        config.headers.authorization = `Bearer ${access}`;
    }
    return config;
});
client.interceptors.response.use((response) => response, async (error) => {
    const original = error.config;
    if (error?.response?.status === 401 && !original?._retry && getRefreshToken()) {
        if (isRefreshing)
            throw error;
        isRefreshing = true;
        original._retry = true;
        try {
            const { data } = await axios.post(`${baseURL}/api/v1/auth/refresh`, {
                refresh_token: getRefreshToken()
            });
            setTokens(data);
            isRefreshing = false;
            return client(original);
        }
        catch (refreshError) {
            isRefreshing = false;
            clearTokens();
            throw refreshError;
        }
    }
    throw error;
});
export async function login(payload) {
    const { data } = await client.post("/api/v1/auth/login", payload);
    setTokens(data);
    return data;
}
export async function register(payload) {
    const { data } = await client.post("/api/v1/auth/register", payload);
    return data;
}
export async function logout() {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
        await client.post("/api/v1/auth/logout", { refresh_token: refreshToken });
    }
    clearTokens();
}
export async function getMe() {
    const { data } = await client.get("/api/v1/auth/me");
    return data;
}
export function isAuthenticated() {
    return !!getAccessToken();
}
export async function analyzeReviews(payload) {
    const { data } = await client.post("/api/v1/reports/analyze", payload);
    return data;
}
export async function getTaskStatus(taskId) {
    const { data } = await client.get(`/api/v1/reports/status/${taskId}`);
    return data;
}
export async function getReport(taskId) {
    const { data } = await client.get(`/api/v1/reports/${taskId}`);
    return data;
}
