import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Shield, Lock, User, Eye, EyeOff, AlertCircle, Loader2 } from "lucide-react";
import { useAuth } from "../../../contexts/AuthContext";
import { apiClient } from "../../../services/api";

const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
  rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setErrorMsg(null);
    try {
      // 1. Authenticate and get tokens
      const loginRes = await apiClient.post("/auth/login", {
        username: data.username,
        password: data.password,
      });

      const { access_token } = loginRes.data.data;

      // Ensure the interceptor can pick it up immediately
      localStorage.setItem("sentinel_token", access_token);
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      // 2. Fetch the current user profile
      const meRes = await apiClient.get("/auth/me", {
        headers: {
          Authorization: `Bearer ${access_token}`
        }
      });
      const user = meRes.data.data;

      // 3. Store in context and local storage (handled by login fn)
      login(access_token, user);

    } catch (error) {
      console.error("Login failed:", error);
      setErrorMsg("Invalid username or password");
      delete apiClient.defaults.headers.common["Authorization"];
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-primary-container rounded-xl flex items-center justify-center shadow-lg shadow-primary/10">
            <Shield className="w-10 h-10 text-on-primary-container" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-headline-lg font-headline-lg text-on-surface">
          Endpoint Sentinel <span className="text-primary">X</span>
        </h2>
        <p className="mt-2 text-center text-body-sm text-on-surface-variant">
          Enterprise Security Console
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-surface-container-low py-8 px-4 shadow-xl shadow-black/10 border border-outline-variant sm:rounded-xl sm:px-10">
          
          {errorMsg && (
            <div className="mb-6 p-4 rounded-md bg-error/15 border border-error flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-error flex-shrink-0 mt-0.5" />
              <p className="text-body-sm text-error">{errorMsg}</p>
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label htmlFor="username" className="block text-label-md font-label-md text-on-surface mb-1">
                Username
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-on-surface-variant" />
                </div>
                <input
                  id="username"
                  type="text"
                  autoComplete="username"
                  autoFocus
                  className={`block w-full pl-10 pr-3 py-2 border ${
                    errors.username ? "border-error focus:ring-error focus:border-error" : "border-outline-variant focus:ring-primary focus:border-primary"
                  } rounded-lg bg-surface-container-high text-on-surface focus:outline-none focus:ring-1 sm:text-body-sm transition-colors`}
                  placeholder="admin"
                  {...register("username")}
                />
              </div>
              {errors.username && (
                <p className="mt-1 text-label-sm text-error">{errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-label-md font-label-md text-on-surface mb-1">
                Password
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-on-surface-variant" />
                </div>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  className={`block w-full pl-10 pr-10 py-2 border ${
                    errors.password ? "border-error focus:ring-error focus:border-error" : "border-outline-variant focus:ring-primary focus:border-primary"
                  } rounded-lg bg-surface-container-high text-on-surface focus:outline-none focus:ring-1 sm:text-body-sm transition-colors`}
                  placeholder="••••••••"
                  {...register("password")}
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-on-surface-variant hover:text-on-surface focus:outline-none transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
              {errors.password && (
                <p className="mt-1 text-label-sm text-error">{errors.password.message}</p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-primary focus:ring-primary border-outline-variant bg-surface-container-high rounded cursor-pointer"
                  {...register("rememberMe")}
                />
                <label htmlFor="remember-me" className="ml-2 block text-body-sm text-on-surface-variant cursor-pointer">
                  Remember me
                </label>
              </div>

              <div className="text-body-sm">
                <a href="#" onClick={(e) => e.preventDefault()} className="font-medium text-primary hover:text-primary/80 transition-colors">
                  Forgot your password?
                </a>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex justify-center items-center gap-2 py-2 px-4 border border-transparent rounded-lg shadow-sm text-body-sm font-bold text-on-primary bg-primary hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Authenticating...
                  </>
                ) : (
                  "Sign in"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
