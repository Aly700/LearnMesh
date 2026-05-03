import { render, screen } from "@testing-library/react";
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
});
