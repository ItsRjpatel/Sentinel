import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../services/api";

interface User {
  id: string;
  username: string;
  roles: string[];
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem("sentinel_token");
      const storedUser = localStorage.getItem("sentinel_user");

      if (storedToken) {
        setToken(storedToken);
        apiClient.defaults.headers.common["Authorization"] = `Bearer ${storedToken}`;

        if (storedUser) {
          try {
            setUser(JSON.parse(storedUser));
          } catch (e) {
            console.error("Failed to parse stored user", e);
          }
        }

        try {
          // Restore and validate user from GET /auth/me
          const meRes = await apiClient.get("/auth/me");
          const validatedUser = meRes.data.data;
          setUser(validatedUser);
          localStorage.setItem("sentinel_user", JSON.stringify(validatedUser));
        } catch (error) {
          console.error("Token verification failed during startup:", error);
          // Token is invalid - clear storage and state
          setToken(null);
          setUser(null);
          localStorage.removeItem("sentinel_token");
          localStorage.removeItem("sentinel_user");
          delete apiClient.defaults.headers.common["Authorization"];
        }
      }

      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem("sentinel_token", newToken);
    localStorage.setItem("sentinel_user", JSON.stringify(newUser));
    apiClient.defaults.headers.common["Authorization"] = `Bearer ${newToken}`;
    navigate("/");
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("sentinel_token");
    localStorage.removeItem("sentinel_user");
    delete apiClient.defaults.headers.common["Authorization"];
    navigate("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!token,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
