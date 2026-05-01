import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { fetchSyndicatedLearningPaths } from "../lib/api";
import { SyndicatedLearningPathSummary } from "../lib/types";

const SyndicatedPathCard = ({
  path,
}: {
  path: SyndicatedLearningPathSummary;
}) => {
  return (
    <article className="path-card">
      <div className="path-card-header">
        <h3>{path.title}</h3>
        <span className="type-pill">{path.step_count} steps</span>
      </div>
      <p className="path-summary">{path.description}</p>
      <div className="meta-row">
        <span>{path.estimated_minutes_total} min</span>
        <span>{path.step_count} lessons</span>
      </div>
      <Link
        className="inline-link"
        to={`/syndication/learning-paths/${path.slug}`}
      >
        Open syndicated path
      </Link>
    </article>
  );
};

export const SyndicatedLearningPathsPage = () => {
  const [items, setItems] = useState<SyndicatedLearningPathSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    fetchSyndicatedLearningPaths()
      .then((data) => {
        if (isActive) {
          setItems(data.items);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(
            currentError.message || "Unable to load syndicated learning paths.",
          );
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, []);

  return (
    <>
      <section className="surface page-header">
        <span className="eyebrow">Syndication</span>
        <h2>Public learning paths.</h2>
        <p>
          Partner-facing read-only view of learning paths whose ordered steps
          resolve to published content.
        </p>
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Syndicated Path Feed</h3>
          <span className="footer-note">
            Slim summaries by design &mdash; follow up on a path for the full
            ordered-steps payload.
          </span>
        </div>

        {error ? (
          <EmptyState title="Syndicated paths unavailable" message={error} />
        ) : loading ? (
          <LoadingState
            title="Loading syndicated paths"
            message="Fetching the public learning-path feed."
          />
        ) : items.length === 0 ? (
          <EmptyState
            title="No syndicated paths yet"
            message="No learning paths currently expose any published steps."
          />
        ) : (
          <div className="path-grid">
            {items.map((path) => (
              <SyndicatedPathCard key={path.slug} path={path} />
            ))}
          </div>
        )}
      </section>
    </>
  );
};
