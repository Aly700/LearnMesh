import { useMemo } from "react";

import { useProgressIndex } from "../lib/progressIndex";
import { LearningPathStep } from "../lib/types";

interface PathProgress {
  completed: number;
  total: number;
}

export function usePathProgress(steps: LearningPathStep[]): PathProgress {
  const { statusFor } = useProgressIndex();

  return useMemo(() => {
    let completed = 0;
    for (const step of steps) {
      if (statusFor(step.content_type, step.content_id) === "completed") {
        completed++;
      }
    }
    return { completed, total: steps.length };
  }, [steps, statusFor]);
}
