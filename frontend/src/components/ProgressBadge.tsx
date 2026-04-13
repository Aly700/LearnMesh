import { ProgressStatus } from "../lib/types";

interface ProgressBadgeProps {
  status: ProgressStatus;
}

const LABELS: Record<ProgressStatus, string> = {
  not_started: "Not started",
  in_progress: "In progress",
  completed: "Completed",
};

export const ProgressBadge = ({ status }: ProgressBadgeProps) => {
  return (
    <span className={`progress-badge progress-badge-${status}`}>
      {LABELS[status]}
    </span>
  );
};
