import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Shield, Lock, User, Eye, EyeOff, AlertCircle } from "lucide-react";
import { useAuth } from "../../../contexts/AuthContext";
import { apiClient } from "../../../services/api";
import { Button, Input, Card } from "../../../components/ui";

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
      username: "",
      password: "",
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

      // 2. Fetch current user profile
      const meRes = await apiClient.get("/auth/me", {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });
      const user = meRes.data.data;

      // 3. Store in auth context & storage
      login(access_token, user);
    } catch (error) {
      console.error("Login failed:", error);
      setErrorMsg("Invalid username or password");
      delete apiClient.defaults.headers.common["Authorization"];
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8 select-none">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-primary/10 border border-primary/30 rounded-2xl flex items-center justify-center shadow-lg shadow-primary/10">
            <Shield className="w-10 h-10 text-primary" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-headline-lg font-bold text-on-surface">
          Endpoint Sentinel <span className="text-primary">X</span>
        </h2>
        <p className="mt-2 text-center text-body-sm text-on-surface-variant">
          Enterprise Security & EDR Console
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card className="sm:px-10 py-8 shadow-xl">
          {errorMsg && (
            <div className="mb-6 p-4 rounded-lg bg-error/15 border border-error/30 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-error flex-shrink-0 mt-0.5" />
              <p className="text-body-sm text-error">{errorMsg}</p>
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)} autoComplete="off">
            <Input
              label="Username"
              placeholder="Enter username"
              leftIcon={<User className="h-5 w-5" />}
              error={errors.username?.message}
              autoComplete="username"
              autoFocus
              {...register("username")}
            />

            <Input
              label="Password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              leftIcon={<Lock className="h-5 w-5" />}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-on-surface-variant hover:text-on-surface focus:outline-none transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
              error={errors.password?.message}
              autoComplete="current-password"
              {...register("password")}
            />

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
                <Link
                  to="/forgot-password"
                  className="font-medium text-primary hover:underline transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
            </div>

            <Button type="submit" isLoading={isSubmitting} className="w-full">
              Sign in to Console
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
