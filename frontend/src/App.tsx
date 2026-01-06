import { Routes, Route, Navigate } from "react-router-dom";
import { Component as LandingPage } from "@/pages/landing";
import Chatbot from "@/pages/chatbot";
import Settings from "@/pages/settings";
import { AppLayout } from "@/components/layout/app-layout";
import LoginPage from "@/pages/login";
import SignupPage from "@/pages/signup";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import { APP_CONFIG } from '@/config/app.config';

// Protected route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth();

  // Bypass login if configured (for development)
  if (APP_CONFIG.dev.bypassLogin) {
    return <>{children}</>;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
const WithLayout = ({ children }: { children: React.ReactNode }) => (
  <AppLayout>{children}</AppLayout>
);

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Landing page - no sidebar */}
        <Route path="/" element={<LandingPage />} />

        {/* Auth pages - redirect to home if bypass enabled */}
        <Route 
          path="/login" 
          element={
            APP_CONFIG.dev.bypassLogin 
              ? <Navigate to="/chatbot" replace /> 
              : <LoginPage />
          } 
        />
        <Route 
          path="/signup" 
          element={
            APP_CONFIG.dev.bypassLogin 
              ? <Navigate to="/" replace /> 
              : <SignupPage />
          } 
        />

        {/* Protected pages with sidebar layout */}
        <Route
          path="/chatbot"
          element={
            <ProtectedRoute>
              <WithLayout>
                <Chatbot />
              </WithLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <WithLayout>
                <Settings />
              </WithLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </AuthProvider>
  );
}
