interface SourceTagProps {
  label: string;
  platform?: "personal" | "substack" | "medium" | "portfolio";
  url?: string | null;
}

export function SourceTag({ label, platform = "personal", url }: SourceTagProps) {
  const className = `source-tag ${platform}`;

  if (url) {
    return (
      <a className={className} href={url} target="_blank" rel="noopener noreferrer">
        {label}
      </a>
    );
  }
  return <span className={className}>{label}</span>;
}