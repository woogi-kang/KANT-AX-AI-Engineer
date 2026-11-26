import { LEVELS, type LevelName } from "@/lib/meta";

export default function Level({ level, title = true }: { level: LevelName; title?: boolean }) {
  return (
    <span className={`lvl l${LEVELS[level]}`} title={title ? `레벨 ${level}` : undefined}>
      <i />
      <i />
      <i />
      {level}
    </span>
  );
}
