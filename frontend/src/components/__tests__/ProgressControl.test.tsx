import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ProgressControl } from "../ProgressControl";

describe("ProgressControl", () => {
  it("calls onChange when a non-active option is clicked", async () => {
    const onChange = vi.fn();
    render(
      <ProgressControl
        status="not_started"
        loading={false}
        updating={false}
        error={null}
        onChange={onChange}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "In progress" }));
    expect(onChange).toHaveBeenCalledWith("in_progress");
  });

  it("disables the active option and marks it aria-pressed", () => {
    render(
      <ProgressControl
        status="completed"
        loading={false}
        updating={false}
        error={null}
        onChange={vi.fn()}
      />,
    );

    const active = screen.getByRole("button", { name: "Completed" });
    expect(active).toBeDisabled();
    expect(active).toHaveAttribute("aria-pressed", "true");
  });
});
