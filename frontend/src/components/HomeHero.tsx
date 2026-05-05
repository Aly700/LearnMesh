import { Link } from "react-router-dom";

const MeshBackground = () => (
  <>
    <div className="hero-mesh-bg" aria-hidden="true" />
    <svg
      className="hero-mesh-svg"
      aria-hidden="true"
      focusable="false"
      viewBox="0 0 800 400"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <pattern
          id="hero-mesh-dots"
          x="0"
          y="0"
          width="26"
          height="26"
          patternUnits="userSpaceOnUse"
        >
          <circle cx="1" cy="1" r="1" fill="rgba(148, 163, 184, 0.18)" />
        </pattern>
        <linearGradient id="hero-mesh-edge" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor="rgba(34, 211, 238, 0)" />
          <stop offset="0.5" stopColor="rgba(34, 211, 238, 0.55)" />
          <stop offset="1" stopColor="rgba(124, 58, 237, 0)" />
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#hero-mesh-dots)" />
      <g
        stroke="url(#hero-mesh-edge)"
        strokeWidth="1.1"
        fill="none"
        strokeLinecap="round"
      >
        <line x1="120" y1="80" x2="280" y2="160" />
        <line x1="280" y1="160" x2="460" y2="100" />
        <line x1="280" y1="160" x2="380" y2="280" />
        <line x1="460" y1="100" x2="640" y2="180" />
        <line x1="380" y1="280" x2="560" y2="320" />
        <line x1="640" y1="180" x2="720" y2="280" />
        <line x1="120" y1="80" x2="100" y2="240" />
      </g>
      <g fill="rgba(34, 211, 238, 0.65)">
        <circle cx="120" cy="80" r="3" />
        <circle cx="280" cy="160" r="4" />
        <circle cx="460" cy="100" r="3" />
        <circle cx="380" cy="280" r="3" />
        <circle cx="640" cy="180" r="4" />
        <circle cx="720" cy="280" r="3" />
        <circle cx="560" cy="320" r="3" />
        <circle cx="100" cy="240" r="3" />
      </g>
    </svg>
  </>
);

export const HomeHero = () => (
  <section className="surface showcase hero-section">
    <MeshBackground />
    <div className="hero-content">
      <span className="eyebrow hero-rise hero-rise-delay-1">
        LearnMesh — Developer Education
      </span>
      <h2 className="hero-headline hero-rise hero-rise-delay-2">
        Learn through{" "}
        <span className="hero-headline-accent">connection</span>, not
        memorization.
      </h2>
      <p className="hero-lede hero-rise hero-rise-delay-2">
        A graph-shaped learning platform that links courses, tutorials, and
        labs into guided paths — so the next concept is always one edge away
        from what you just learned.
      </p>
      <div className="hero-actions hero-rise hero-rise-delay-3">
        <Link className="primary-link-button" to="/explore">
          Explore the catalog
        </Link>
        <Link className="secondary-link-button" to="/learning-paths">
          Browse learning paths
        </Link>
      </div>
    </div>
  </section>
);
