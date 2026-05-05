import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ContentCard } from "../components/ContentCard";
import { EmptyState } from "../components/EmptyState";
import { HomeDashboardPreview } from "../components/HomeDashboardPreview";
import { HomeFeatureGrid } from "../components/HomeFeatureGrid";
import { HomeHero } from "../components/HomeHero";
import { LoadingState } from "../components/LoadingState";
import { usePathProgress } from "../hooks/usePathProgress";
import { fetchCatalog, fetchLearningPaths } from "../lib/api";
import { useAuth } from "../lib/auth";
import { ContentSummary, LearningPath } from "../lib/types";

const HomePathCard = ({ path }: { path: LearningPath }) => {
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
        {path.ordered_content.slice(0, 3).map((item) => (
          <li key={item.id}>
            {item.content_title}{" "}
            <span className="footer-note">({item.content_type})</span>
          </li>
        ))}
      </ol>
      <Link className="inline-link" to={`/learning-paths/${path.slug}`}>
        Open learning path
      </Link>
    </article>
  );
};

export const HomePage = () => {
  const [catalog, setCatalog] = useState<ContentSummary[]>([]);
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    Promise.all([
      fetchCatalog({ status: "published" }),
      fetchLearningPaths(),
    ])
      .then(([catalogItems, learningPathItems]) => {
        if (isActive) {
          setCatalog(catalogItems);
          setLearningPaths(learningPathItems);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(currentError.message || "Unable to load dashboard data.");
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, []);

  const totalMinutes = catalog.reduce(
    (minutes, item) => minutes + item.estimated_minutes,
    0,
  );
  const featuredContent = catalog.slice(0, 3);
  const recentContent = catalog.slice(3, 7);
  const featuredPaths = learningPaths.slice(0, 3);

  return (
    <>
      <HomeHero />

      <HomeDashboardPreview
        catalog={catalog}
        learningPaths={learningPaths}
        loading={loading}
      />

      <HomeFeatureGrid />

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Platform Snapshot</h3>
          <span className="footer-note">
            Seeded data keeps the MVP immediately demoable.
          </span>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <strong>{loading ? "..." : catalog.length}</strong>
            <span>Total content items</span>
          </div>
          <div className="stat-card">
            <strong>{loading ? "..." : featuredPaths.length}</strong>
            <span>Featured paths</span>
          </div>
          <div className="stat-card">
            <strong>{loading ? "..." : totalMinutes}</strong>
            <span>Total learning minutes</span>
          </div>
          <div className="stat-card">
            <strong>{loading ? "..." : learningPaths.length}</strong>
            <span>Learning paths</span>
          </div>
        </div>
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Featured Content</h3>
          <span className="footer-note">
            A mix of structured courses, quick tutorials, and hands-on labs.
          </span>
        </div>

        {error ? (
          <EmptyState title="Dashboard unavailable" message={error} actionLabel="Open explore" actionTo="/explore" />
        ) : loading ? (
          <LoadingState
            title="Loading featured content"
            message="Fetching the latest published learning content."
          />
        ) : (
          <div className="highlights-grid">
            {featuredContent.map((item) => (
              <ContentCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Guided Learning Paths</h3>
          <span className="footer-note">
            Curated sequences turn standalone lessons into coherent journeys.
          </span>
        </div>

        {error ? (
          <EmptyState title="Learning paths unavailable" message={error} />
        ) : loading ? (
          <LoadingState
            title="Loading learning paths"
            message="Pulling together the guided path library."
          />
        ) : learningPaths.length === 0 ? (
          <EmptyState
            title="No learning paths yet"
            message="Create a path once there is enough content to curate."
          />
        ) : (
          <div className="path-grid">
            {featuredPaths.map((path) => (
              <HomePathCard key={path.id} path={path} />
            ))}
          </div>
        )}
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Recently Added</h3>
          <span className="footer-note">
            New material across backend, frontend, cloud-native, and LLM topics.
          </span>
        </div>

        {loading ? (
          <LoadingState
            title="Loading recent content"
            message="Preparing the latest catalog additions."
          />
        ) : recentContent.length === 0 ? (
          <EmptyState
            title="No recent content"
            message="Seed more content to expand the catalog."
          />
        ) : (
          <div className="content-grid">
            {recentContent.map((item) => (
              <ContentCard item={item} key={`${item.content_type}-${item.id}`} />
            ))}
          </div>
        )}
      </section>
    </>
  );
};
