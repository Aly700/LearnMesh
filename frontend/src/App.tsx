import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { ContentCollectionPage } from "./pages/ContentCollectionPage";
import { ContentDetailPage } from "./pages/ContentDetailPage";
import { ExplorePage } from "./pages/ExplorePage";
import { HomePage } from "./pages/HomePage";
import { LearningPathDetailPage } from "./pages/LearningPathDetailPage";
import { LearningPathsPage } from "./pages/LearningPathsPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { SearchPage } from "./pages/SearchPage";
import { SyndicatedContentDetailPage } from "./pages/SyndicatedContentDetailPage";
import { SyndicatedContentFeedPage } from "./pages/SyndicatedContentFeedPage";
import { SyndicatedLearningPathDetailPage } from "./pages/SyndicatedLearningPathDetailPage";
import { SyndicatedLearningPathsPage } from "./pages/SyndicatedLearningPathsPage";

const App = () => {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/explore" element={<ExplorePage />} />
        <Route
          path="/courses"
          element={
            <ContentCollectionPage
              resource="courses"
              title="Courses"
              description="Structured developer education designed to help learners move from fundamentals to practical delivery."
            />
          }
        />
        <Route
          path="/courses/:slug"
          element={<ContentDetailPage resource="courses" />}
        />
        <Route
          path="/tutorials"
          element={
            <ContentCollectionPage
              resource="tutorials"
              title="Tutorials"
              description="Shorter guided walkthroughs that help developers ship a focused outcome quickly."
            />
          }
        />
        <Route
          path="/tutorials/:slug"
          element={<ContentDetailPage resource="tutorials" />}
        />
        <Route
          path="/labs"
          element={
            <ContentCollectionPage
              resource="labs"
              title="Labs"
              description="Hands-on exercises for practicing workflows, tooling, and platform-building fundamentals."
            />
          }
        />
        <Route path="/labs/:slug" element={<ContentDetailPage resource="labs" />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/learning-paths" element={<LearningPathsPage />} />
        <Route
          path="/learning-paths/:slug"
          element={<LearningPathDetailPage />}
        />
        <Route
          path="/syndication/learning-paths"
          element={<SyndicatedLearningPathsPage />}
        />
        <Route
          path="/syndication/learning-paths/:slug"
          element={<SyndicatedLearningPathDetailPage />}
        />
        <Route
          path="/syndication/content"
          element={<SyndicatedContentFeedPage />}
        />
        <Route
          path="/syndication/content/:contentType/:slug"
          element={<SyndicatedContentDetailPage />}
        />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<Navigate replace to="/" />} />
      </Route>
    </Routes>
  );
};

export default App;
