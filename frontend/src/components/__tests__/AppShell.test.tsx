import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

vi.mock("../../lib/auth", () => ({
  useAuth: () => ({
    user: null,
    loading: false,
    logout: () => {},
  }),
}));

import { AppShell } from "../AppShell";

describe("AppShell primary nav", () => {
  it("renders the Public Syndication section with both links", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <AppShell />
      </MemoryRouter>,
    );

    expect(screen.getByText("Public Syndication")).toBeInTheDocument();

    const contentLink = screen.getByRole("link", { name: "Syndicated Content" });
    expect(contentLink).toHaveAttribute("href", "/syndication/content");

    const pathsLink = screen.getByRole("link", { name: "Syndicated Paths" });
    expect(pathsLink).toHaveAttribute("href", "/syndication/learning-paths");
  });

  it("toggles the mobile nav panel via the disclosure button", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <AppShell />
      </MemoryRouter>,
    );

    const toggle = screen.getByRole("button", { name: /open navigation/i });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(toggle).toHaveAttribute("aria-controls", "primary-nav");

    const panel = document.getElementById("primary-nav");
    expect(panel).not.toBeNull();
    expect(panel).toHaveAttribute("data-open", "false");

    await userEvent.click(toggle);

    const openToggle = screen.getByRole("button", { name: /close navigation/i });
    expect(openToggle).toHaveAttribute("aria-expanded", "true");
    expect(panel).toHaveAttribute("data-open", "true");
    expect(screen.getByText("Public Syndication")).toBeInTheDocument();
  });
});
