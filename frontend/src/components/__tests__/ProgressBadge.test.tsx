import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { ProgressBadge } from "../ProgressBadge";

describe("ProgressBadge", () => {
  it("renders the in-progress label", () => {
    render(<ProgressBadge status="in_progress" />);
    expect(screen.getByText("In progress")).toBeInTheDocument();
  });

  it("applies the status-specific class", () => {
    render(<ProgressBadge status="completed" />);
    const badge = screen.getByText("Completed");
    expect(badge).toHaveClass("progress-badge");
    expect(badge).toHaveClass("progress-badge-completed");
  });
});
