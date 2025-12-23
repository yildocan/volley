import { Link } from "react-router-dom";

export function InfoPage() {
  return (
    <div className="w-full max-w-xl space-y-6 rounded-3xl bg-white/80 p-8 shadow-lift rise-in">
      <div className="space-y-2 text-center">
        <h1 className="font-display text-3xl font-semibold text-steel">VoleyTeamMaker</h1>
        <p className="text-sm text-steel/70">
          Takım dağıtımı, oyuncuların aldığı ortalama puanlara göre dengeli olacak şekilde
          oluşturulur.
        </p>
      </div>

      <div className="space-y-3 text-sm text-steel/80">
        <p>Algoritmanın basit özeti:</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>Herkesin aldığı ortalama puan hesaplanır.</li>
          <li>Oyuncular puana göre sıralanır.</li>
          <li>İki takım puan ve cinsiyet dengesini koruyacak şekilde dağıtılır.</li>
          <li>Gerekirse küçük takaslarla denge daha da iyileştirilir.</li>
        </ul>
      </div>

      <div className="flex justify-center">
        <Link
          className="rounded-full bg-steel px-5 py-2 text-sm font-semibold text-white shadow-glow transition hover:bg-steel/90"
          to="/login"
        >
          Giriş ekranına dön
        </Link>
      </div>
    </div>
  );
}
