type GenderBadgeProps = {
  gender: "M" | "F";
};

export function GenderBadge({ gender }: GenderBadgeProps) {
  const color = gender === "M" ? "bg-tide" : "bg-coral";
  return (
    <span
      className={`inline-flex h-8 w-8 items-center justify-center rounded-full ${color} text-xs font-semibold text-white`}
    >
      {gender}
    </span>
  );
}
