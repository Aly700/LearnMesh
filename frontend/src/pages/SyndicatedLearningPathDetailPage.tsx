import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { fetchSyndicatedLearningPathDetail } from "../lib/api";
import { formatLabel } from "../lib/content";
import { SyndicatedLearningPathDetail } from "../lib/types";

export const SyndicatedLearningPathDetailPage = () => {
  const { slug } = useParams();
  const [path, setPath] = useState<SyndicatedLearningPathDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) {
      return;
    }

    let isActive = true;
    setLoading(true);
    setError(null);

    fetchSyndicatedLearningPathDetail(slug)
      .then((data) => {
        if (isActive) {
          setPath(data);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(
            currentError.message || "Unable to load syndicated learning path.",
          );
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [slug]);

  if (error) {
    return (
      <section className="surface page-section">
        <EmptyState
          title="Syndicated path unavailable"
          message={error}
          actionLabel="Back to syndicated paths"
          actionTo="/syndication/learning-paths"
        />
      </section>
    );
  }

  if (loading || !path) {
    return (
      <section className="surface page-section">
        <LoadingState
          title="Loading syndicated path"
          message="Fetching the public ordered-steps payload."
        />
      </section>
    );
  }

  return (
    <>
      <section className="surface detail-hero">
        <div>
          <span className="eyebrow">Syndicated Learning Path</span>
          <h2>{path.title}</h2>
          <p>{path.description}</p>
          <div className="meta-row">
            <span>{path.step_count} steps</span>
            <span>{path.estimated_minutes_total} min</span>
          </div>
        </div>

        <aside className="detail-side-panel">
          <div className="detail-side-card">
            <strong>Quick navigation</strong>
            <ul className="quick-nav-list">
              {path.steps.map((step) => (
                <li key={`${step.position}-${step.slug}`}>
                  <a href={`#step-${step.position}`}>
                    Step {step.position}: {step.title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </aside>
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Path Timeline</h3>
          <span className="footer-note">
            Reference-only steps &mdash; partners follow up via the public
            content endpoint for full per-step detail.
          </span>
        </div>

        <div className="timeline-list">
          {path.steps.map((step) => (
            <article
              className="timeline-step"
              id={`step-${step.position}`}
              key={`${step.position}-${step.slug}`}
            >
              <div className="timeline-marker">
                {String(step.position).padStart(2, "0")}
              </div>
              <div className="timeline-body">
                <div className="card-kicker-row">
                  <span className="type-pill">
                    {formatLabel(step.content_type)}
                  </span>
                </div>
                <h3>{step.title}</h3>
                <p className="panel-subtitle">
                  Slug: <code>{step.slug}</code>
                </p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </>
  );
};
