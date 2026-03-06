"use client";

import { useUser } from "@clerk/nextjs";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

export default function DashboardPage() {
  const { user } = useUser();
  const [healthStatus, setHealthStatus] = useState<string>("checking...");

  useEffect(() => {
    apiFetch("/api/health/")
      .then((data) => setHealthStatus(data.status))
      .catch(() => setHealthStatus("error - is the backend running?"));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-2">Welcome</h2>
          <p className="text-gray-600">
            Hello, {user?.firstName || user?.emailAddresses[0]?.emailAddress}!
          </p>
        </div>
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold mb-2">Backend Status</h2>
          <p className="text-gray-600">
            API Health:{" "}
            <span
              className={
                healthStatus === "healthy"
                  ? "text-green-600 font-medium"
                  : "text-red-600 font-medium"
              }
            >
              {healthStatus}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
