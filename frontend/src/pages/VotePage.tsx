import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { apiRequest } from "../api";
import { GenderBadge } from "../components/GenderBadge";
import { useAuth } from "../context/AuthContext";

type UserItem = {
  id: string;
  username: string;
  gender: "M" | "F";
};

export function VotePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { token, userId } = useAuth();
  const [users, setUsers] = useState<UserItem[]>([]);
  const [scores, setScores] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [progress, setProgress] = useState({ completed: 0, required: 12 });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const loadUsers = async () => {
      if (!id) {
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const data = await apiRequest<UserItem[]>(`/events/${id}/participants`, {}, token);
        const filtered = data.filter((user) => user.id !== userId);
        if (mounted) {
          setUsers(filtered);
          const defaults: Record<string, number> = {};
          filtered.forEach((user) => {
            defaults[user.id] = 5;
          });
          setScores(defaults);
        }
      } catch (err) {
        if (mounted) {
          setError((err as Error).message);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadUsers();
    return () => {
      mounted = false;
    };
  }, [id, token, userId]);

  const loadProgress = async () => {
    if (!id) {
      return;
    }
    try {
      const data = await apiRequest<{ completed_voters: number; required_voters: number }>(
        `/events/${id}/progress`,
        {},
        token
      );
      setProgress({ completed: data.completed_voters, required: data.required_voters });
    } catch (err) {
      setError((err as Error).message);
    }
  };

  useEffect(() => {
    let mounted = true;
    const refresh = async () => {
      if (!mounted) {
        return;
      }
      await loadProgress();
    };
    refresh();
    const interval = setInterval(refresh, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [id, token]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!id) {
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      for (const user of users) {
        await apiRequest(
          `/events/${id}/votes`,
          {
            method: "POST",
            body: JSON.stringify({
              target_user_id: user.id,
              score: scores[user.id] || 5
            })
          },
          token
        );
      }
      await loadProgress();
      navigate(`/events/${id}/teams`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <p className="text-steel/70">Oyuncular yükleniyor...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="space-y-2">
          <p className="text-sm uppercase tracking-[0.3em] text-steel/60">Oy verme</p>
          <h2 className="font-display text-3xl font-semibold text-steel">
            Her oyuncuyu puanlayın
          </h2>
        </div>
        <p className="max-w-md text-sm text-steel/70">
          Diğer oyunculara 1-10 arası puan verin. Skorlar takımları dengeleyecek.
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-white/70 p-4 shadow-glow">
        <div>
          <p className="text-sm font-semibold text-steel">Sonuç Göster</p>
          <p className="text-xs text-steel/70">{progress.completed} kişi oy kullandı</p>
        </div>
        <button
          type="button"
          onClick={() => navigate(`/events/${id}/teams`)}
          disabled={progress.completed < progress.required}
          className={`w-full rounded-full px-5 py-2 text-sm font-semibold shadow-glow transition sm:w-auto ${
            progress.completed < progress.required
              ? "cursor-not-allowed bg-steel/30 text-steel/60"
              : "bg-steel text-white hover:bg-steel/90"
          }`}
        >
          Sonuç Göster ({progress.completed} kişi oy kullandı)
        </button>
      </div>

      {error ? <p className="text-sm text-coral">{error}</p> : null}

      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="grid gap-4">
          {users.map((user) => (
            <div
              key={user.id}
              className="rounded-3xl border border-white/60 bg-white/80 p-5 shadow-glow"
            >
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <GenderBadge gender={user.gender} />
                  <div>
                    <p className="font-semibold text-steel">{user.username}</p>
                    <p className="text-xs text-steel/60">Performans puanını ayarla</p>
                  </div>
                </div>
                <span className="rounded-full bg-clay px-3 py-1 text-xs font-semibold text-steel">
                  {scores[user.id] ?? 5}
                </span>
              </div>
              <input
                type="range"
                min={1}
                max={10}
                value={scores[user.id] ?? 5}
                onChange={(event) =>
                  setScores((prev) => ({
                    ...prev,
                    [user.id]: Number(event.target.value)
                  }))
                }
                className="mt-4 w-full accent-coral"
              />
            </div>
          ))}
        </div>

        <button
          type="submit"
          className="rounded-full bg-steel px-6 py-3 text-sm font-semibold text-white shadow-glow transition hover:bg-steel/90"
          disabled={submitting}
        >
          {submitting ? "Oylar gönderiliyor..." : "Oyları gönder"}
        </button>
      </form>
    </div>
  );
}
