import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

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
      const data = await apiRequest<{
        access_token: string;
        username: string;
        user_id: string;
        is_admin: boolean;
      }>(
        "/auth/login",
        {
          method: "POST",
          body: JSON.stringify({ username })
        }
      );
      login(data.access_token, data.username, data.user_id, data.is_admin);
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
        <h1 className="font-display text-3xl font-semibold text-steel">VoleyTeamMaker</h1>
        <p className="text-sm text-steel/70">
          Bu uygulama voleybolda eşit şekilde takımlar oluşturmak için tasarlanmıştır,
          algoritma ve çalışma mantığı için aşağıdaki butondan inceleyebilirsiniz.
        </p>
      </div>

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="text-sm font-medium text-steel">İsim</label>
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
          {loading ? "Giriş yapılıyor..." : "Giriş yap"}
        </button>
      </form>

      <Link
        className="w-full rounded-2xl border border-steel/15 px-4 py-3 text-center text-sm font-semibold text-steel transition hover:border-steel/40"
        to="/info"
      >
        Bilgi sayfası
      </Link>
    </div>
  );
}
