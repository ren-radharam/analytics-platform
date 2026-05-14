import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

api.interceptors.response.use(
  (r) => r,
  async (err: AxiosError) => {
    const original = err.config as RetriableConfig | undefined;
    const is401 = err.response?.status === 401;
    const isRefreshCall = original?.url?.includes("/auth/refresh");

    if (
      is401 &&
      typeof window !== "undefined" &&
      original &&
      !original._retry &&
      !isRefreshCall
    ) {
      original._retry = true;
      try {
        const { data } = await axios.post<{ access_token: string }>(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`,
          {},
          { withCredentials: true },
        );
        localStorage.setItem("access_token", data.access_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
    }

    return Promise.reject(err);
  },
);

export default api;
