import { CSSProperties } from "react";
import { Link } from "react-router-dom";

import { useContinueLearning } from "../hooks/useContinueLearning";
import { usePathProgress } from "../hooks/usePathProgress";
import { formatLabel, getContentHref } from "../lib/content";
import { useAuth } from "../lib/auth";
import { ContentSummary, LearningPath, ProgressListItem } from "../lib/types";

interface HomeDashboardPreviewProps {
  catalog: ContentSummary[];
  learningPaths: LearningPath[];
  loading: boolean;
}

const PathProgressStrip = ({ path }: { path: LearningPath }) => {
  const { completed, total } = usePathProgress(path.ordered_content);
  const percent =
    total > 0 ? Math.min(100, Math.round((completed / total) * 100)) : 0;

  return (
    <div className="dashboard-preview-card path-progress-strip">
      <span className="dashboard-preview-kicker">Path progress</span>
      <h4>{path.title}</h4>
      <p className="dashboard-preview-meta">
        {completed} of {total} lessons complete · {path.estimated_minutes_total}{" "}
        min total
      </p>
      <div className="dashboard-preview-progress" aria-hidden="true">
        <div
          className="dashboard-preview-progress-fill"
          style={{ "--progress": `${percent}%` } as CSSProperties}
        />
      </div>
      <Link className="inline-link" to={`/learning-paths/${path.slug}`}>
        Open path
      </Link>
    </div>
  );
};

const InProgressCard = ({ item }: { item: ProgressListItem }) => (
  <Link
    className="dashboard-preview-card dashboard-preview-link"
    to={getContentHref(item.content)}
  >
    <span className="dashboard-preview-kicker">In progress</span>
    <h4>{item.content.title}</h4>
    <p className="dashboard-preview-meta">
      {formatLabel(item.content.content_type)} ·{" "}
      {item.content.estimated_minutes} min · {formatLabel(item.content.difficulty)}
    </p>
  </Link>
);

const RecommendedCard = ({ item }: { item: ContentSummary }) => (
  <Link
    className="dashboard-preview-card dashboard-preview-link"
    to={getContentHref(item)}
  >
    <span className="dashboard-preview-kicker">Recommended</span>
    <h4>{item.title}</h4>
    <p className="dashboard-preview-meta">
      {formatLabel(item.content_type)} · {item.estimated_minutes} min ·{" "}
      {formatLabel(item.difficulty)}
    </p>
  </Link>
);

export const HomeDashboardPreview = ({
  catalog,
  learningPaths,
  loading,
}: HomeDashboardPreviewProps) => {
  const { user } = useAuth();
  const continueLearning = useContinueLearning();

  const featuredPath = learningPaths[0];
  const recommendedPicks = catalog.slice(0, 3);
  const inProgressPicks = continueLearning.items.slice(0, 3);

  const headlineCopy = user
    ? "Your dashboard"
    : "What your dashboard looks like";
  const subCopy = user
    ? "Pick up where you left off and track progress across guided paths."
    : "Sign in to track progress and continue lessons across devices — here's the shape of it.";

  return (
    <section className="surface showcase page-section dashboard-preview-section">
      <div className="section-heading dashboard-preview-heading">
        <div>
          <span className="dashboard-preview-kicker">Live preview</span>
          <h3>{headlineCopy}</h3>
        </div>
        <span className="footer-note showcase-footer-note">{subCopy}</span>
      </div>

      {loading && recommendedPicks.length === 0 ? (
        <div className="dashboard-preview-empty">
          Loading the latest catalog…
        </div>
      ) : (
        <div className="dashboard-preview-grid">
          {user && inProgressPicks.length > 0
            ? inProgressPicks.map((item) => (
                <InProgressCard
                  key={`${item.content_type}-${item.content_id}`}
                  item={item}
                />
              ))
            : recommendedPicks.map((item) => (
                <RecommendedCard key={item.id} item={item} />
              ))}
          {featuredPath ? <PathProgressStrip path={featuredPath} /> : null}
        </div>
      )}

      {user && !continueLearning.loading && inProgressPicks.length === 0 ? (
        <p className="dashboard-preview-meta dashboard-preview-hint">
          No items in progress yet — start one from the catalog and it will land
          here.
        </p>
      ) : null}
    </section>
  );
};
