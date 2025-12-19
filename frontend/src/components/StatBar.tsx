type StatBarProps = {
  label: string;
  value: number;
  max: number;
  colorClass: string;
};

export function StatBar({ label, value, max, colorClass }: StatBarProps) {
  const width = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm text-steel">
        <span>{label}</span>
        <span className="font-semibold">{value.toFixed(1)}</span>
      </div>
      <div className="h-3 w-full rounded-full bg-mist">
        <div
          className={`h-3 rounded-full ${colorClass}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}
