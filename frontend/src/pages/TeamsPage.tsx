import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { apiRequest } from "../api";
import { GenderBadge } from "../components/GenderBadge";
import { StatBar } from "../components/StatBar";
import { useAuth } from "../context/AuthContext";

type ScoreItem = {
  user_id: string;
  username: string;
  gender: "M" | "F";
  average_score: number;
};

type TeamStats = {
  total_score: number;
  average_score: number;
  gender_counts: { M: number; F: number };
};

type TeamResponse = {
  team_a: ScoreItem[];
  team_b: ScoreItem[];
  summary: { team_a: TeamStats; team_b: TeamStats };
};

export function TeamsPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const [data, setData] = useState<TeamResponse | null>(null);
  const [eventDate, setEventDate] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const loadTeams = async () => {
      if (!id) {
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const event = await apiRequest<{ date: string }>(`/events/${id}`, {}, token);
        const response = await apiRequest<TeamResponse>(`/events/${id}/teams`, {}, token);
        if (mounted) {
          setEventDate(event.date);
          setData(response);
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

    loadTeams();
    return () => {
      mounted = false;
    };
  }, [id, token]);

  if (loading) {
    return <p className="text-steel/70">Takımlar oluşturuluyor...</p>;
  }

  if (error) {
    return (
      <div className="rounded-3xl bg-white/80 p-6 text-sm text-coral shadow-glow">
        {error}
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const maxScore = Math.max(data.summary.team_a.total_score, data.summary.team_b.total_score);
  const formattedDate = eventDate
    ? new Date(eventDate).toLocaleDateString(undefined, {
        weekday: "long",
        month: "short",
        day: "numeric",
        year: "numeric"
      })
    : null;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="space-y-2">
          <p className="text-sm uppercase tracking-[0.3em] text-steel/60">Takım dağılımı</p>
          <h2 className="font-display text-3xl font-semibold text-steel">Dengeli takımlar</h2>
          {formattedDate ? (
            <p className="text-sm text-steel/70">
              {formattedDate} tarihi için takımlar bu şekilde seçildi.
            </p>
          ) : null}
        </div>
        <div className="rounded-2xl bg-white/70 px-4 py-2 text-sm text-steel shadow-glow">
          Cinsiyet dengesi: {data.summary.team_a.gender_counts.M}M/
          {data.summary.team_a.gender_counts.F}F
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <TeamCard title="Takım A" accent="bg-coral" members={data.team_a} />
          <TeamCard title="Takım B" accent="bg-tide" members={data.team_b} />
        </div>

        <div className="space-y-4 rounded-3xl bg-white/80 p-6 shadow-lift">
          <h3 className="font-display text-xl text-steel">Takım gücü</h3>
          <StatBar
            label="Takım A toplam"
            value={data.summary.team_a.total_score}
            max={maxScore}
            colorClass="bg-coral"
          />
          <StatBar
            label="Takım B toplam"
            value={data.summary.team_b.total_score}
            max={maxScore}
            colorClass="bg-tide"
          />
          <div className="rounded-2xl bg-clay px-4 py-3 text-sm text-steel/80">
            Ortalama skorlar: A {data.summary.team_a.average_score.toFixed(2)} | B{" "}
            {data.summary.team_b.average_score.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
}

function TeamCard({
  title,
  accent,
  members
}: {
  title: string;
  accent: string;
  members: ScoreItem[];
}) {
  return (
    <div className="rounded-3xl bg-white/80 p-6 shadow-lift">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-xl text-steel">{title}</h3>
        <span className={`h-3 w-12 rounded-full ${accent}`} />
      </div>
      <div className="mt-4 space-y-3">
        {members.map((member) => (
          <div
            key={member.user_id}
            className="flex items-center justify-between rounded-2xl border border-white/70 bg-white/70 px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <GenderBadge gender={member.gender} />
              <div>
                <p className="font-semibold text-steel">{member.username}</p>
                <p className="text-xs text-steel/60">Ort. puan {member.average_score.toFixed(1)}</p>
              </div>
            </div>
            <span className="rounded-full bg-mist px-3 py-1 text-xs font-semibold text-steel">
              {member.average_score.toFixed(1)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
