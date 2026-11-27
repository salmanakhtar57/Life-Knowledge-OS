
import type { SourcePlatform } from "../types/api";

interface SourceTagProps {
  label: string;
  platform?: SourcePlatform;
  url?: string | null;
}

export function SourceTag({
  label,
  platform = "personal",
  url,
}: SourceTagProps) {
  const className = `source-tag ${platform}`;

  const content = (
    <>
      {platform === "substack" && <span className="tag-mark">▰</span>}
      {platform === "medium" && <span className="tag-mark medium-mark">M</span>}
      {platform === "personal" && <span className="tag-mark">▤</span>}
      <span>{label}</span>
    </>
  );

  if (url) {
    return (
      <a
        className={className}
        href={url}
        target="_blank"
        rel="noopener noreferrer"
      >
        {content}
      </a>
    );
  }

  return <span className={className}>{content}</span>;
}
