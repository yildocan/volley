import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { apiRequest } from "../api";
import { GenderBadge } from "../components/GenderBadge";
import { useAuth } from "../context/AuthContext";

type EventItem = {
  id: string;
  date: string;
  weekly_recurrence: boolean;
};

type UserItem = {
  id: string;
  username: string;
  gender: "M" | "F";
};

export function EventsPage() {
  const { token, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState(() =>
    new Date().toISOString().split("T")[0]
  );
  const [events, setEvents] = useState<EventItem[]>([]);
  const [users, setUsers] = useState<UserItem[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedCount = useMemo(
    () => Object.values(selectedUsers).filter(Boolean).length,
    [selectedUsers]
  );

  useEffect(() => {
    if (!token) {
      return;
    }

    const loadEvents = async () => {
      try {
        const data = await apiRequest<EventItem[]>("/events", {}, token);
        setEvents(data);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    const loadUsers = async () => {
      try {
        const data = await apiRequest<UserItem[]>("/users", {}, token);
        setUsers(data);
        const defaults: Record<string, boolean> = {};
        data.forEach((user) => {
          defaults[user.id] = true;
        });
        setSelectedUsers(defaults);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    loadEvents();
    if (isAdmin) {
      loadUsers();
    }
  }, [token, isAdmin]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const selected = new Date(`${selectedDate}T00:00:00`);
      if (Number.isNaN(selected.getTime()) || selected.getDay() !== 4) {
        setError("Yalnız Perşembe günleri oy kullanabilirsiniz.");
        setLoading(false);
        return;
      }
      const selectedIds = Object.keys(selectedUsers).filter((id) => selectedUsers[id]);
      if (selectedIds.length < 12) {
        setError("En az 12 kişi seçilmelidir.");
        setLoading(false);
        return;
      }
      const payload = { date: selectedDate, weekly_recurrence: false };
      const created = await apiRequest<EventItem>(
        "/events",
        {
          method: "POST",
          body: JSON.stringify(payload)
        },
        token
      );
      await apiRequest(
        `/events/${created.id}/participants`,
        {
          method: "PUT",
          body: JSON.stringify({ user_ids: selectedIds })
        },
        token
      );
      navigate(`/events/${created.id}/vote`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (!isAdmin) {
    return (
      <div className="space-y-8">
        <section className="space-y-3">
          <p className="text-sm uppercase tracking-[0.3em] text-steel/60">Etkinlik</p>
          <h2 className="font-display text-3xl font-semibold text-steel">Maç tarihleri</h2>
        </section>

        {error ? <p className="text-sm text-coral">{error}</p> : null}

        <div className="grid gap-6 md:grid-cols-2">
          {events.map((eventItem) => {
            const date = new Date(eventItem.date);
            return (
              <div
                key={eventItem.id}
                className="rounded-3xl border border-white/50 bg-white/80 p-6 shadow-lift"
              >
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-steel/70">Etkinlik tarihi</p>
                  <h3 className="font-display text-2xl text-steel">
                    {date.toLocaleDateString(undefined, {
                      weekday: "long",
                      month: "short",
                      day: "numeric",
                      year: "numeric"
                    })}
                  </h3>
                </div>
                <div className="mt-6 flex flex-wrap gap-3">
                  <Link
                    className="rounded-full bg-tide px-4 py-2 text-sm font-semibold text-white shadow-glow"
                    to={`/events/${eventItem.id}/vote`}
                  >
                    Oy ver
                  </Link>
                  <Link
                    className="rounded-full border border-steel/15 px-4 py-2 text-sm font-semibold text-steel"
                    to={`/events/${eventItem.id}/teams`}
                  >
                    Sonuçları gör
                  </Link>
                </div>
              </div>
            );
          })}
        </div>

        <p className="rounded-2xl bg-white/70 px-5 py-4 text-sm text-black shadow-glow">
          Sadece perşembe günleri etkinlik olduğu için perşembe günleri oylama
          açabilirsiniz, seçtiğiniz tarih içerisinde etkinliğe katılacak insanları 1-10
          arası puan verdikten sonra, min 12 kişi oy kullandığında takımlar
          görselleşecektir.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <p className="text-sm uppercase tracking-[0.3em] text-steel/60">Yönetici</p>
        <h2 className="font-display text-3xl font-semibold text-steel">Etkinlik oluştur</h2>
        <p className="text-sm text-steel/70">
          Perşembe günleri için katılımcıları seç ve oylamayı başlat.
        </p>
      </section>

      {error ? <p className="text-sm text-coral">{error}</p> : null}

      <form
        onSubmit={handleSubmit}
        className="space-y-6 rounded-3xl border border-white/60 bg-white/80 p-6 shadow-lift"
      >
        <div className="space-y-2">
          <label className="text-sm font-medium text-steel">Maç tarihi</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(event) => setSelectedDate(event.target.value)}
            className="w-full rounded-2xl border border-steel/10 bg-white px-4 py-3 text-steel shadow-sm focus:border-coral focus:outline-none"
            required
          />
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-steel">Katılımcılar</p>
            <span className="rounded-full bg-clay px-3 py-1 text-xs font-semibold text-steel">
              Seçilen: {selectedCount}
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {users.map((user) => (
              <label
                key={user.id}
                className={`flex cursor-pointer items-center justify-between rounded-2xl border px-4 py-3 text-sm transition ${
                  selectedUsers[user.id]
                    ? "border-transparent bg-steel text-white"
                    : "border-steel/15 bg-white text-steel"
                }`}
              >
                <div className="flex items-center gap-3">
                  <GenderBadge gender={user.gender} />
                  <span>{user.username}</span>
                </div>
                <input
                  type="checkbox"
                  checked={selectedUsers[user.id] ?? false}
                  onChange={() =>
                    setSelectedUsers((prev) => ({
                      ...prev,
                      [user.id]: !prev[user.id]
                    }))
                  }
                  className="h-4 w-4 accent-coral"
                />
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="w-full rounded-full bg-tide px-6 py-3 text-sm font-semibold text-white shadow-glow transition hover:bg-tide/90"
          disabled={loading}
        >
          {loading ? "Etkinlik oluşturuluyor..." : "Etkinliği başlat"}
        </button>
      </form>
    </div>
  );
}
