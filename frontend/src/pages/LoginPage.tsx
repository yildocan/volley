import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiRequest } from "../api";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await apiRequest<{ access_token: string; username: string; user_id: string }>(
        "/auth/login",
        {
          method: "POST",
          body: JSON.stringify({ username })
        }
      );
      login(data.access_token, data.username, data.user_id);
      navigate("/events");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-6 rounded-3xl bg-white/80 p-8 shadow-lift rise-in">
      <div className="space-y-2 text-center">
        <h1 className="font-display text-3xl font-semibold text-steel">Welcome back</h1>
        <p className="text-sm text-steel/70">
          Enter your name. Small typos are matched to the closest name.
        </p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="text-sm font-medium text-steel">Username</label>
          <input
            className="w-full rounded-2xl border border-steel/10 bg-white px-4 py-3 text-steel shadow-sm focus:border-coral focus:outline-none"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />
        </div>
        {error ? <p className="text-sm text-coral">{error}</p> : null}
        <button
          type="submit"
          className="w-full rounded-2xl bg-coral px-4 py-3 text-sm font-semibold text-white shadow-glow transition hover:bg-coral/90"
          disabled={loading}
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <p className="text-center text-sm text-steel/70">
        Need a new name? Ask the organizer to add it to the list.
      </p>
    </div>
  );
}
