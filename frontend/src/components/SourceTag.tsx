interface SourceTagProps {
  label: string;
}

export function SourceTag({ label }: SourceTagProps) {
  return <span className="source-tag">{label}</span>;
}
