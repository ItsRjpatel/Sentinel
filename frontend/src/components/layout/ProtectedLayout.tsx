import { Outlet, Navigate } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { GlobalSearchModal } from "./GlobalSearchModal";
import { useAuth } from "../../contexts/AuthContext";

export function ProtectedLayout() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center select-none">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <span className="text-body-sm font-medium text-on-surface-variant">
            Initializing Sentinel X Console...
          </span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-background text-on-background flex flex-col antialiased">
      {/* Global Search Modal (Ctrl+K) */}
      <GlobalSearchModal />

      {/* Fixed Header */}
      <Header />

      {/* Fixed Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="pt-12 min-h-screen flex flex-col flex-1 md:pl-[240px]">
        <div className="w-full p-4 flex-1 flex flex-col">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
