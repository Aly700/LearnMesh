import { ReactNode } from "react";

interface Feature {
  title: string;
  body: string;
  icon: ReactNode;
}

const MeshIcon = (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <circle cx="5" cy="6" r="2" />
    <circle cx="19" cy="6" r="2" />
    <circle cx="12" cy="13" r="2" />
    <circle cx="6" cy="19" r="2" />
    <circle cx="18" cy="19" r="2" />
    <line x1="6.7" y1="7.4" x2="11" y2="11.8" />
    <line x1="17.3" y1="7.4" x2="13" y2="11.8" />
    <line x1="11" y1="14.4" x2="7.3" y2="17.5" />
    <line x1="13" y1="14.4" x2="16.7" y2="17.5" />
  </svg>
);

const PathIcon = (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <circle cx="6" cy="5" r="1.6" />
    <circle cx="18" cy="12" r="1.6" />
    <circle cx="6" cy="19" r="1.6" />
    <path d="M6 6.6 C 6 11, 18 8, 18 12 S 6 13, 6 17.4" />
  </svg>
);

const GaugeIcon = (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <path d="M4 16 A 8 8 0 0 1 20 16" />
    <line x1="12" y1="16" x2="16.5" y2="10.5" />
    <circle cx="12" cy="16" r="1.4" fill="currentColor" stroke="none" />
  </svg>
);

const features: Feature[] = [
  {
    title: "Connected knowledge",
    body: "Courses, tutorials, and labs are linked by shared concepts and tags so each lesson opens a path to the next one.",
    icon: MeshIcon,
  },
  {
    title: "Guided learning paths",
    body: "Curated step-by-step sequences turn isolated lessons into coherent journeys with timing and ordering baked in.",
    icon: PathIcon,
  },
  {
    title: "Progress that follows you",
    body: "Per-item state, per-step state, and path-level rollups travel with your account across every lesson surface.",
    icon: GaugeIcon,
  },
];

export const HomeFeatureGrid = () => (
  <section className="surface showcase page-section feature-section">
    <div className="section-heading">
      <h3>Built for developers, shaped like a graph</h3>
      <span className="footer-note showcase-footer-note">
        Three building blocks LearnMesh is organized around.
      </span>
    </div>
    <div className="feature-grid">
      {features.map((feature) => (
        <article className="feature-card" key={feature.title}>
          <span className="feature-icon" aria-hidden="true">
            {feature.icon}
          </span>
          <h4>{feature.title}</h4>
          <p>{feature.body}</p>
        </article>
      ))}
    </div>
  </section>
);
