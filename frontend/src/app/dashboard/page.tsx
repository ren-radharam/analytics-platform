"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import api from "@/lib/api";
import { useAuthStore } from "@/store/auth";

const BAR_FILL = "#6366f1";

interface EventStats {
  total_events: number;
  top_events: { name: string; count: number }[];
}

interface DashboardSummary {
  id: string;
  name: string;
  is_public: boolean;
}

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const [stats, setStats] = useState<EventStats | null>(null);
  const [dashboards, setDashboards] = useState<DashboardSummary[]>([]);
  const [newDashName, setNewDashName] = useState("");

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, dashRes] = await Promise.all([
        api.get<EventStats>("/events/stats"),
        api.get<DashboardSummary[]>("/dashboards"),
      ]);
      setStats(statsRes.data);
      setDashboards(dashRes.data);
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => {
    if (!user) {
      void router.push("/login");
    }
  }, [user, router]);

  useEffect(() => {
    if (!user) return;
    const id = window.setTimeout(() => {
      void fetchData();
    }, 0);
    return () => clearTimeout(id);
  }, [user, fetchData]);

  const createDashboard = async () => {
    if (!newDashName) return;
    await api.post("/dashboards", { name: newDashName });
    setNewDashName("");
    void fetchData();
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
            <span className="text-sm font-bold text-white">A</span>
          </div>
          <span className="font-semibold text-gray-900">Analytics Platform</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">{user.email}</span>
          <button
            type="button"
            onClick={() => {
              logout();
              router.push("/login");
            }}
            className="text-sm text-red-600 hover:text-red-800"
          >
            Sign out
          </button>
        </div>
      </nav>
      <main className="mx-auto max-w-7xl px-6 py-8">
        <h1 className="mb-6 text-2xl font-bold text-gray-900">Overview</h1>
        <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <p className="mb-1 text-sm text-gray-500">Total Events</p>
            <p className="text-3xl font-bold text-indigo-600">
              {stats?.total_events ?? "—"}
            </p>
          </div>
          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <p className="mb-1 text-sm text-gray-500">Dashboards</p>
            <p className="text-3xl font-bold text-green-600">{dashboards.length}</p>
          </div>
          <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm">
            <p className="mb-1 text-sm text-gray-500">Role</p>
            <p className="text-xl font-bold capitalize text-gray-800">{user.role}</p>
          </div>
        </div>
        {stats && stats.top_events.length > 0 && (
          <div className="mb-8 rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Top Events</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={stats.top_events}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill={BAR_FILL} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">My Dashboards</h2>
          <div className="mb-4 flex gap-2">
            <input
              value={newDashName}
              onChange={(e) => setNewDashName(e.target.value)}
              placeholder="New dashboard name..."
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="button"
              onClick={() => void createDashboard()}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Create
            </button>
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
            {dashboards.map((d) => (
              <div
                key={d.id}
                role="button"
                tabIndex={0}
                onClick={() => router.push(`/dashboard/${d.id}`)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ")
                    router.push(`/dashboard/${d.id}`);
                }}
                className="cursor-pointer rounded-lg border border-gray-200 p-4 transition-colors hover:border-indigo-300 hover:bg-indigo-50"
              >
                <p className="font-medium text-gray-900">{d.name}</p>
                <p className="mt-1 text-xs text-gray-400">
                  {d.is_public ? "Public" : "Private"}
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
