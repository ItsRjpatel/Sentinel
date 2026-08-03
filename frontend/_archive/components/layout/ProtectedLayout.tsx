import { useState, useEffect } from "react";
import { Outlet, Navigate } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useAuth } from "../../contexts/AuthContext";
import { cn } from "../../utils/cn";

export function ProtectedLayout() {
  const { isAuthenticated } = useAuth();
  const [isPinned, setIsPinned] = useState(() => {
    const stored = localStorage.getItem("sentinel_sidebar_pinned");
    return stored !== null ? JSON.parse(stored) : true;
  });

  useEffect(() => {
    localStorage.setItem("sentinel_sidebar_pinned", JSON.stringify(isPinned));
  }, [isPinned]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  const marginLeft = isPinned ? "md:ml-[280px]" : "md:ml-[72px]";

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Sidebar isPinned={isPinned} setIsPinned={setIsPinned} />
      <main 
        className={cn(
          "pt-14 min-h-screen bg-background transition-all duration-300 ml-0",
          marginLeft
        )}
      >
        <div className="p-container-padding">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
