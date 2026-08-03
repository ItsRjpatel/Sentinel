import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedLayout } from "./components/layout/ProtectedLayout";
import { LoginForm } from "./features/auth/components/LoginForm";
import { ForgotPassword } from "./features/auth/pages/ForgotPassword";
import { EndpointDetailsPage } from "./features/endpoints/details/pages/EndpointDetailsPage";
import {
  DashboardPage,
  EndpointsPage,
  CommandsPage,
  AlertsPage,
  UsersPage,
  RolesPage,
  PermissionsPage,
  SettingsPage,
  AuditLogsPage,
  DocsPage,
  ReportsPage,
  OrganizationPage,
  SoftwarePage,
} from "./pages";

const queryClient = new QueryClient();

import { LiveConsolePage } from "./features/console/pages/LiveConsolePage";
import { GroupsPage } from "./features/groups/pages/GroupsPage";
import { GroupDetailsPage } from "./features/groups/pages/GroupDetailsPage";
import { PoliciesPage } from "./features/policies/pages/PoliciesPage";
import { PolicyDetailsPage } from "./features/policies/pages/PolicyDetailsPage";
import { SchedulesPage } from "./features/schedules/pages/SchedulesPage";
import { NotificationsPage } from "./features/notifications/pages/NotificationsPage";

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <ThemeProvider>
          <AuthProvider>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<LoginForm />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />

              {/* Protected Routes */}
              <Route element={<ProtectedLayout />}>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/endpoints" element={<EndpointsPage />} />
                <Route path="/endpoints/:id" element={<EndpointDetailsPage />} />
                <Route path="/groups" element={<GroupsPage />} />
                <Route path="/groups/:id" element={<GroupDetailsPage />} />
                <Route path="/commands" element={<CommandsPage />} />
                <Route path="/console" element={<LiveConsolePage />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/policies" element={<PoliciesPage />} />
                <Route path="/policies/:id" element={<PolicyDetailsPage />} />
                <Route path="/schedules" element={<SchedulesPage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/audit" element={<AuditLogsPage />} />
                <Route path="/roles" element={<RolesPage />} />
                <Route path="/permissions" element={<PermissionsPage />} />
                <Route path="/admin/users" element={<UsersPage />} />
                <Route path="/admin/roles" element={<RolesPage />} />
                <Route path="/admin/permissions" element={<PermissionsPage />} />
                <Route path="/admin/settings" element={<SettingsPage />} />
                <Route path="/admin/audit" element={<AuditLogsPage />} />
                <Route path="/docs" element={<DocsPage />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/organization" element={<OrganizationPage />} />
                <Route path="/software" element={<SoftwarePage />} />
                {/* Fallback */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
