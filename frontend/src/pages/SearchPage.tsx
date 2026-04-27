import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { ContentCard } from "../components/ContentCard";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { searchContent } from "../lib/api";
import { ContentType, SearchResponse } from "../lib/types";

const CONTENT_TYPE_OPTIONS: Array<{ value: ContentType | "all"; label: string }> = [
  { value: "all", label: "All types" },
  { value: "course", label: "Courses" },
  { value: "tutorial", label: "Tutorials" },
  { value: "lab", label: "Labs" },
];

export const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlQuery = searchParams.get("q") ?? "";
  const urlContentType =
    (searchParams.get("content_type") as ContentType | "all" | null) ?? "all";

  const [inputValue, setInputValue] = useState(urlQuery);
  const [contentType, setContentType] = useState<ContentType | "all">(urlContentType);
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setInputValue(urlQuery);
    setContentType(urlContentType);
  }, [urlQuery, urlContentType]);

  useEffect(() => {
    if (urlQuery.trim().length < 2) {
      setResponse(null);
      setError(null);
      setLoading(false);
      return;
    }

    let isActive = true;
    setLoading(true);
    setError(null);

    searchContent(
      urlQuery,
      urlContentType === "all" ? undefined : urlContentType,
    )
      .then((data) => {
        if (isActive) {
          setResponse(data);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(currentError.message || "Search failed.");
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [urlQuery, urlContentType]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = inputValue.trim();
    const next = new URLSearchParams();
    if (trimmed.length >= 2) {
      next.set("q", trimmed);
    }
    if (contentType !== "all") {
      next.set("content_type", contentType);
    }
    setSearchParams(next);
  }

  const showPrompt = urlQuery.trim().length < 2;

  return (
    <>
      <section className="surface page-header">
        <span className="eyebrow">Search</span>
        <h2>Find a course, tutorial, or lab.</h2>
        <p>
          Ranked across title, tags, description, and author. Only published
          content is searched.
        </p>

        <form className="search-form" onSubmit={handleSubmit} role="search">
          <input
            type="search"
            className="search-input"
            placeholder="Search by keyword..."
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            minLength={2}
            maxLength={200}
            aria-label="Search query"
          />
          <select
            className="search-type-select"
            value={contentType}
            onChange={(event) =>
              setContentType(event.target.value as ContentType | "all")
            }
            aria-label="Filter by content type"
          >
            {CONTENT_TYPE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <button type="submit" className="primary-link-button">
            Search
          </button>
        </form>
      </section>

      <section className="surface page-section">
        {showPrompt ? (
          <EmptyState
            title="Start typing to search"
            message="Enter at least two characters and press Search."
          />
        ) : error ? (
          <EmptyState
            title="Search failed"
            message={error}
            actionLabel="Back to dashboard"
            actionTo="/"
          />
        ) : loading ? (
          <LoadingState
            title="Searching"
            message={`Looking for "${urlQuery}" across the catalog.`}
          />
        ) : !response || response.total === 0 ? (
          <EmptyState
            title="No matches"
            message={`No published content matched "${urlQuery}".`}
          />
        ) : (
          <>
            <div className="section-heading">
              <h3>
                Showing {response.results.length} of {response.total} result
                {response.total === 1 ? "" : "s"} for &quot;{response.query}&quot;
              </h3>
              <span className="footer-note">
                Ranked by weighted matches over title, tags, description, author.
              </span>
            </div>

            <div className="content-grid">
              {response.results.map((result) => (
                <article
                  className="search-result-wrapper"
                  key={`${result.content_type}-${result.id}`}
                >
                  <ContentCard item={result} />
                  <div className="search-result-meta">
                    <span className="search-score">
                      score {result.score.toFixed(1)}
                    </span>
                    <span className="search-matched-fields">
                      matched: {result.matched_fields.join(", ")}
                    </span>
                  </div>
                </article>
              ))}
            </div>
          </>
        )}
      </section>
    </>
  );
};
