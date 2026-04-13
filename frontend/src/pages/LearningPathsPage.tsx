import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { usePathProgress } from "../hooks/usePathProgress";
import { fetchLearningPaths } from "../lib/api";
import { useAuth } from "../lib/auth";
import { LearningPath } from "../lib/types";

const PathCard = ({ path }: { path: LearningPath }) => {
  const { user } = useAuth();
  const { completed, total } = usePathProgress(path.ordered_content);

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
      {user && completed > 0 ? (
        <p className="path-progress-text">{completed} of {total} completed</p>
      ) : null}
      <ol>
        {path.ordered_content.slice(0, 4).map((item) => (
          <li key={item.id}>
            {item.content_title}
            <div className="footer-note">
              {item.content_type} &bull; {item.estimated_minutes} min
            </div>
          </li>
        ))}
      </ol>
      <Link className="inline-link" to={`/learning-paths/${path.slug}`}>
        Open learning path
      </Link>
    </article>
  );
};

export const LearningPathsPage = () => {
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    fetchLearningPaths()
      .then((data) => {
        if (isActive) {
          setPaths(data);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(currentError.message || "Unable to load learning paths.");
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
        <span className="eyebrow">Learning Paths</span>
        <h2>Structured pathways for developers.</h2>
        <p>
          Learning paths group standalone content into ordered sequences that are
          easier to assign, recommend, and demo.
        </p>
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Path Library</h3>
          <span className="footer-note">
            Ordered references are resolved on the backend and returned ready for UI display.
          </span>
        </div>

        {error ? (
          <EmptyState title="Learning paths unavailable" message={error} />
        ) : loading ? (
          <LoadingState
            title="Loading learning paths"
            message="Preparing the guided path library."
          />
        ) : paths.length === 0 ? (
          <EmptyState
            title="No learning paths yet"
            message="Create a path to turn the content catalog into a guided experience."
          />
        ) : (
          <div className="path-grid">
            {paths.map((path) => (
              <PathCard key={path.id} path={path} />
            ))}
          </div>
        )}
      </section>
    </>
  );
};
