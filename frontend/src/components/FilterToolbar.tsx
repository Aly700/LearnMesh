import { formatLabel } from "../lib/content";
import { BrowseFilters, ContentType, Difficulty, Status } from "../lib/types";

interface FilterToolbarProps {
  filters: BrowseFilters;
  availableTags: string[];
  showContentType?: boolean;
  showStatus?: boolean;
  onDifficultyChange: (value: Difficulty | "all") => void;
  onStatusChange: (value: Status | "all") => void;
  onContentTypeChange: (value: ContentType | "all") => void;
  onTagToggle: (tag: string) => void;
  onClear: () => void;
}

export const FilterToolbar = ({
  filters,
  availableTags,
  showContentType = false,
  showStatus = false,
  onDifficultyChange,
  onStatusChange,
  onContentTypeChange,
  onTagToggle,
  onClear,
}: FilterToolbarProps) => {
  return (
    <div className="filter-toolbar">
      <div className="filter-grid">
        <label className="filter-field">
          <span>Difficulty</span>
          <select
            value={filters.difficulty}
            onChange={(event) =>
              onDifficultyChange(event.target.value as Difficulty | "all")
            }
          >
            <option value="all">All levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </label>

        {showContentType ? (
          <label className="filter-field">
            <span>Content type</span>
            <select
              value={filters.content_type}
              onChange={(event) =>
                onContentTypeChange(event.target.value as ContentType | "all")
              }
            >
              <option value="all">All formats</option>
              <option value="course">Course</option>
              <option value="tutorial">Tutorial</option>
              <option value="lab">Lab</option>
            </select>
          </label>
        ) : null}

        {showStatus ? (
          <label className="filter-field">
            <span>Status</span>
            <select
              value={filters.status}
              onChange={(event) =>
                onStatusChange(event.target.value as Status | "all")
              }
            >
              <option value="all">All statuses</option>
              <option value="published">Published</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </label>
        ) : null}

        <button className="secondary-button" onClick={onClear} type="button">
          Clear filters
        </button>
      </div>

      {availableTags.length > 0 ? (
        <div className="filter-tag-group">
          {availableTags.map((tag) => {
            const isActive = filters.tags.includes(tag);
            return (
              <button
                key={tag}
                className={isActive ? "filter-chip active" : "filter-chip"}
                onClick={() => onTagToggle(tag)}
                type="button"
              >
                {formatLabel(tag)}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
};
