import { UserButton } from "@clerk/clerk-react";
import { Link, Outlet } from "react-router";

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-6">
            <Link to="/dashboard" className="text-xl font-bold">
              __PROJECT_NAME__
            </Link>
            <div className="flex gap-4">
              <Link
                to="/dashboard"
                className="text-gray-600 hover:text-gray-900"
              >
                Dashboard
              </Link>
            </div>
          </div>
          <UserButton />
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
