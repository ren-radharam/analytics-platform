import { create } from "zustand";
import { persist } from "zustand/middleware";

import api from "@/lib/api";

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  org_id: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    fullName: string,
    orgName: string,
  ) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      login: async (email, password) => {
        const { data } = await api.post("/auth/login", { email, password });
        localStorage.setItem("access_token", data.access_token);
        set({ user: data.user, token: data.access_token });
      },
      register: async (email, password, full_name, org_name) => {
        const { data } = await api.post("/auth/register", {
          email,
          password,
          full_name,
          org_name,
        });
        localStorage.setItem("access_token", data.access_token);
        set({ user: data.user, token: data.access_token });
      },
      logout: () => {
        localStorage.removeItem("access_token");
        set({ user: null, token: null });
      },
    }),
    {
      name: "auth-storage",
      partialize: (s) => ({ user: s.user, token: s.token }),
    },
  ),
);
