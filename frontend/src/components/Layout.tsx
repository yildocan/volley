import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function AppLayout() {
  const { token, username, logout } = useAuth();

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute -top-16 -left-24 h-72 w-72 rounded-full bg-coral/20 blur-3xl float-orb" />
      <div className="pointer-events-none absolute bottom-10 right-0 h-80 w-80 rounded-full bg-tide/20 blur-3xl float-orb" />

      <header className="relative z-10 mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
        <Link to="/events" className="font-display text-xl font-semibold text-steel">
          VolleyMatch
        </Link>
        {token ? (
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-white/70 px-4 py-1 text-sm shadow-glow">
              {username}
            </span>
            <button
              className="rounded-full border border-steel/20 px-4 py-1 text-sm text-steel transition hover:border-steel/40"
              onClick={logout}
            >
              Logout
            </button>
          </div>
        ) : null}
      </header>

      <main className="relative z-10 mx-auto w-full max-w-6xl px-6 pb-16">
        <Outlet />
      </main>
    </div>
  );
}

export function AuthLayout() {
  return (
    <div className="relative min-h-screen">
      <div className="pointer-events-none absolute -top-24 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-coral/30 blur-3xl float-orb" />
      <div className="pointer-events-none absolute bottom-0 left-16 h-64 w-64 rounded-full bg-tide/25 blur-3xl float-orb" />
      <div className="relative z-10 flex min-h-screen items-center justify-center px-6">
        <Outlet />
      </div>
    </div>
  );
}
