import { ProgressStatus } from "../lib/types";

interface ProgressControlProps {
  status: ProgressStatus;
  loading: boolean;
  updating: boolean;
  error: string | null;
  onChange: (next: ProgressStatus) => void;
}

const OPTIONS: { value: ProgressStatus; label: string }[] = [
  { value: "not_started", label: "Not started" },
  { value: "in_progress", label: "In progress" },
  { value: "completed", label: "Completed" },
];

export const ProgressControl = ({
  status,
  loading,
  updating,
  error,
  onChange,
}: ProgressControlProps) => {
  return (
    <div className="detail-progress-block">
      <span className="eyebrow">Your progress</span>
      <div className="progress-control" role="group" aria-label="Progress status">
        {OPTIONS.map((option) => {
          const isActive = option.value === status;
          return (
            <button
              key={option.value}
              type="button"
              className={`progress-option${isActive ? " active" : ""}`}
              onClick={() => onChange(option.value)}
              disabled={loading || updating || isActive}
              aria-pressed={isActive}
            >
              {option.label}
            </button>
          );
        })}
      </div>
      {error ? <p className="auth-error">{error}</p> : null}
    </div>
  );
};
