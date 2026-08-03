import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Shield, Mail, ArrowLeft, Info } from "lucide-react";
import { Button, Input, Card } from "../../../components/ui";

export function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [submittedMessage, setSubmittedMessage] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // TODO: Connect to backend password reset API endpoint (e.g. POST /api/v1/auth/forgot-password)
    // Example:
    // await apiClient.post('/auth/forgot-password', { email });

    setSubmittedMessage(
      "Password reset functionality will be implemented in a future sprint."
    );
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8 select-none">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-14 h-14 bg-primary/10 border border-primary/30 rounded-2xl flex items-center justify-center shadow-lg shadow-primary/10">
            <Shield className="w-8 h-8 text-primary" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-headline-lg font-bold text-on-surface">
          Reset your password
        </h2>
        <p className="mt-2 text-center text-body-sm text-on-surface-variant max-w-sm mx-auto">
          Enter your registered email address. We&apos;ll send you instructions to reset your password.
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card className="sm:px-10 py-8 shadow-xl">
          {submittedMessage ? (
            <div className="space-y-6">
              <div className="p-4 rounded-lg bg-primary/10 border border-primary/30 flex items-start gap-3">
                <Info className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <p className="text-body-sm text-on-surface font-medium">
                  {submittedMessage}
                </p>
              </div>

              <div className="text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 text-body-sm font-medium text-primary hover:underline transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Login
                </Link>
              </div>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit}>
              <Input
                label="Email address"
                type="email"
                required
                placeholder="name@organization.com"
                leftIcon={<Mail className="h-5 w-5" />}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                autoFocus
              />

              <Button type="submit" className="w-full">
                Send Reset Link
              </Button>

              <div className="text-center pt-2">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 text-body-sm font-medium text-on-surface-variant hover:text-on-surface transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Login
                </Link>
              </div>
            </form>
          )}
        </Card>
      </div>
    </div>
  );
}
