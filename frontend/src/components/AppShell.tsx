import { FormEvent, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../lib/auth";

interface NavItem {
  to: string;
  label: string;
  end?: boolean;
}

interface NavSection {
  label?: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    items: [
      { to: "/", label: "Dashboard", end: true },
      { to: "/explore", label: "Explore" },
      { to: "/search", label: "Search" },
      { to: "/courses", label: "Courses" },
      { to: "/tutorials", label: "Tutorials" },
      { to: "/labs", label: "Labs" },
      { to: "/learning-paths", label: "Learning Paths" },
    ],
  },
  {
    label: "Public Syndication",
    items: [
      { to: "/syndication/content", label: "Syndicated Content" },
      { to: "/syndication/learning-paths", label: "Syndicated Paths" },
    ],
  },
];

export const AppShell = () => {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarQuery, setSidebarQuery] = useState("");

  function handleSidebarSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = sidebarQuery.trim();
    if (trimmed.length < 2) {
      return;
    }
    navigate(`/search?q=${encodeURIComponent(trimmed)}`);
    setSidebarQuery("");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <span className="brand-mark">LM</span>
          <h1>LearnMesh</h1>
          <p>Developer education, structured like a modern product catalog.</p>
        </div>

        <form
          className="sidebar-search"
          onSubmit={handleSidebarSearch}
          role="search"
        >
          <input
            type="search"
            className="sidebar-search-input"
            placeholder="Search catalog..."
            value={sidebarQuery}
            onChange={(event) => setSidebarQuery(event.target.value)}
            minLength={2}
            maxLength={200}
            aria-label="Search the catalog"
          />
        </form>

        <nav className="nav-list" aria-label="Primary">
          {navSections.map((section, sectionIndex) => (
            <div
              className="nav-section"
              key={section.label ?? `nav-section-${sectionIndex}`}
            >
              {section.label ? (
                <span className="nav-section-label">{section.label}</span>
              ) : null}
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  className={({ isActive }) =>
                    isActive ? "nav-link active" : "nav-link"
                  }
                  end={item.end}
                  to={item.to}
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="account-block">
          {loading ? (
            <span className="account-status">Loading...</span>
          ) : user ? (
            <>
              <span className="account-label">Signed in as</span>
              <span className="account-email">{user.email}</span>
              <button
                type="button"
                className="secondary-button account-button"
                onClick={logout}
              >
                Sign out
              </button>
            </>
          ) : (
            <div className="account-actions">
              <Link to="/login" className="secondary-button account-button">
                Sign in
              </Link>
              <Link to="/register" className="inline-link account-register-link">
                Create account
              </Link>
            </div>
          )}
        </div>

        <div className="sidebar-footer">
          Phase 2 adds detail views, markdown-based lessons, richer browsing, and
          learning paths that feel closer to a real platform.
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};
