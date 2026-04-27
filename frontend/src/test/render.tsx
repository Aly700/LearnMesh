import { ReactElement, ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { render, RenderOptions } from "@testing-library/react";

import {
  ProgressIndexContext,
  ProgressIndexContextValue,
} from "../lib/progressIndex";
import { ContentType, ProgressStatus } from "../lib/types";

const noop = async () => {};

export const emptyProgressIndex: ProgressIndexContextValue = {
  statusFor: () => undefined,
  refresh: noop,
  loading: false,
  error: null,
};

export function progressIndexFromMap(
  entries: Record<string, ProgressStatus>,
): ProgressIndexContextValue {
  return {
    statusFor: (contentType?: ContentType, contentId?: number) => {
      if (!contentType || !contentId) return undefined;
      return entries[`${contentType}:${contentId}`];
    },
    refresh: noop,
    loading: false,
    error: null,
  };
}

interface RenderWithProvidersOptions extends Omit<RenderOptions, "wrapper"> {
  initialEntries?: string[];
  progressIndex?: ProgressIndexContextValue;
}

export function renderWithProviders(
  ui: ReactElement,
  {
    initialEntries = ["/"],
    progressIndex = emptyProgressIndex,
    ...options
  }: RenderWithProvidersOptions = {},
) {
  const Wrapper = ({ children }: { children: ReactNode }) => (
    <MemoryRouter initialEntries={initialEntries}>
      <ProgressIndexContext.Provider value={progressIndex}>
        {children}
      </ProgressIndexContext.Provider>
    </MemoryRouter>
  );

  return render(ui, { wrapper: Wrapper, ...options });
}
