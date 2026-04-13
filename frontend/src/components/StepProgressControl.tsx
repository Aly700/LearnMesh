import { useCallback, useState } from "react";

import { updateMyProgress } from "../lib/api";
import { useProgressIndex } from "../lib/progressIndex";
import { ContentType, ProgressStatus } from "../lib/types";

interface StepProgressControlProps {
  contentType: ContentType;
  contentId: number;
}

const OPTIONS: { value: ProgressStatus; label: string }[] = [
  { value: "not_started", label: "Not started" },
  { value: "in_progress", label: "In progress" },
  { value: "completed", label: "Completed" },
];

export const StepProgressControl = ({
  contentType,
  contentId,
}: StepProgressControlProps) => {
  const { statusFor, refresh } = useProgressIndex();
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentStatus: ProgressStatus = statusFor(contentType, contentId) ?? "not_started";

  const handleChange = useCallback(
    async (next: ProgressStatus) => {
      setUpdating(true);
      setError(null);
      try {
        await updateMyProgress({
          content_type: contentType,
          content_id: contentId,
          status: next,
        });
        await refresh();
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unable to update progress.";
        setError(message);
      } finally {
        setUpdating(false);
      }
    },
    [contentType, contentId, refresh],
  );

  return (
    <div className="step-progress-control">
      <div className="step-progress-buttons" role="group" aria-label="Step progress">
        {OPTIONS.map((option) => {
          const isActive = option.value === currentStatus;
          return (
            <button
              key={option.value}
              type="button"
              className={`step-progress-option${isActive ? " active" : ""}`}
              onClick={() => void handleChange(option.value)}
              disabled={updating || isActive}
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
