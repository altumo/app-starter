import { currentUser } from "@clerk/nextjs/server";
import { db } from "@/lib/db";
import { sql } from "drizzle-orm";

export default async function DashboardPage() {
  const user = await currentUser();

  let dbStatus = "disconnected";
  try {
    await db.execute(sql`SELECT 1`);
    dbStatus = "connected";
  } catch {
    dbStatus = "disconnected";
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Welcome, {user?.firstName || "User"}
        </h2>
        <p className="mt-2 text-gray-600">
          You are signed in as {user?.emailAddresses[0]?.emailAddress}
        </p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          System Status
        </h3>
        <div className="flex items-center gap-2">
          <span
            className={`w-3 h-3 rounded-full ${
              dbStatus === "connected" ? "bg-green-500" : "bg-red-500"
            }`}
          />
          <span className="text-gray-700">Database: {dbStatus}</span>
        </div>
      </div>
    </div>
  );
}
