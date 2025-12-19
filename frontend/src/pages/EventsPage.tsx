import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiRequest } from "../api";

export function EventsPage() {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState(() =>
    new Date().toISOString().split("T")[0]
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const selected = new Date(`${selectedDate}T00:00:00`);
      if (Number.isNaN(selected.getTime()) || selected.getDay() !== 4) {
        setError("Yalniz Persembe gunleri oy kullanilabilir.");
        setLoading(false);
        return;
      }
      const payload = { date: selectedDate, weekly_recurrence: false };
      const data = await apiRequest<{ id: string }>("/events", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      navigate(`/events/${data.id}/vote`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <p className="text-sm uppercase tracking-[0.3em] text-steel/60">Upcoming sessions</p>
        <h2 className="font-display text-3xl font-semibold text-steel">Pick the match date</h2>
      </section>

      {error ? <p className="text-sm text-coral">{error}</p> : null}

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-4 rounded-3xl border border-white/60 bg-white/80 p-6 shadow-lift md:flex-row md:items-end"
      >
        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium text-steel">Match date</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(event) => setSelectedDate(event.target.value)}
            className="w-full rounded-2xl border border-steel/10 bg-white px-4 py-3 text-steel shadow-sm focus:border-coral focus:outline-none"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full rounded-full bg-tide px-6 py-3 text-sm font-semibold text-white shadow-glow transition hover:bg-tide/90 md:w-auto"
          disabled={loading}
        >
          {loading ? "Creating event..." : "Continue to voting"}
        </button>
      </form>
    </div>
  );
}
