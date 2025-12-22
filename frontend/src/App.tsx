import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";

import { AuthProvider, useAuth } from "./context/AuthContext";
import { AppLayout, AuthLayout } from "./components/Layout";
import { EventsPage } from "./pages/EventsPage";
import { InfoPage } from "./pages/InfoPage";
import { LoginPage } from "./pages/LoginPage";
import { TeamsPage } from "./pages/TeamsPage";
import { VotePage } from "./pages/VotePage";

function RequireAuth({ children }: { children: React.ReactElement }) {
  const { token } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

function IndexRedirect() {
  const { token } = useAuth();
  return <Navigate to={token ? "/events" : "/login"} replace />;
}

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<IndexRedirect />} />
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/info" element={<InfoPage />} />
          </Route>
          <Route
            element={
              <RequireAuth>
                <AppLayout />
              </RequireAuth>
            }
          >
            <Route path="/events" element={<EventsPage />} />
            <Route path="/events/:id/vote" element={<VotePage />} />
            <Route path="/events/:id/teams" element={<TeamsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
