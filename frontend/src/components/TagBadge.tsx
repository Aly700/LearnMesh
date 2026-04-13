import { formatLabel } from "../lib/content";

interface TagBadgeProps {
  label: string;
}

export const TagBadge = ({ label }: TagBadgeProps) => {
  return <span className="tag-badge">{formatLabel(label)}</span>;
};
