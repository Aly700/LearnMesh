import { FormEvent, useCallback, useEffect, useState } from "react";
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

const MOBILE_QUERY = "(max-width: 1040px)";

export const AppShell = () => {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarQuery, setSidebarQuery] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mql = window.matchMedia(MOBILE_QUERY);
    const update = () => setIsMobile(mql.matches);
    update();
    mql.addEventListener("change", update);
    return () => mql.removeEventListener("change", update);
  }, []);

  const closeMobileNav = useCallback(() => setMobileOpen(false), []);

  function handleSidebarSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = sidebarQuery.trim();
    if (trimmed.length < 2) {
      return;
    }
    navigate(`/search?q=${encodeURIComponent(trimmed)}`);
    setSidebarQuery("");
    closeMobileNav();
  }

  function handleLogout() {
    logout();
    closeMobileNav();
  }

  const collapsibleHidden = isMobile && !mobileOpen;

  return (
    <div className="app-shell" data-mobile-open={mobileOpen ? "true" : "false"}>
      <header className="app-shell-mobile-bar">
        <Link to="/" className="mobile-bar-brand" onClick={closeMobileNav}>
          <span className="brand-mark">LM</span>
          <span className="mobile-bar-wordmark">LearnMesh</span>
        </Link>
        <button
          type="button"
          className="mobile-bar-toggle"
          aria-expanded={mobileOpen}
          aria-controls="primary-nav"
          aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
          onClick={() => setMobileOpen((v) => !v)}
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
            focusable="false"
          >
            {mobileOpen ? (
              <>
                <line x1="6" y1="6" x2="18" y2="18" />
                <line x1="18" y1="6" x2="6" y2="18" />
              </>
            ) : (
              <>
                <line x1="4" y1="7" x2="20" y2="7" />
                <line x1="4" y1="12" x2="20" y2="12" />
                <line x1="4" y1="17" x2="20" y2="17" />
              </>
            )}
          </svg>
        </button>
      </header>

      <aside
        className="sidebar"
        id="primary-nav"
        data-open={mobileOpen ? "true" : "false"}
        aria-hidden={collapsibleHidden}
      >
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
                  onClick={closeMobileNav}
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
                onClick={handleLogout}
              >
                Sign out
              </button>
            </>
          ) : (
            <div className="account-actions">
              <Link
                to="/login"
                className="secondary-button account-button"
                onClick={closeMobileNav}
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="inline-link account-register-link"
                onClick={closeMobileNav}
              >
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
