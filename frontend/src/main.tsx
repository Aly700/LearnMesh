import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import { AuthProvider } from "./lib/auth";
import { ProgressIndexProvider } from "./lib/progressIndex";
import "./styles/global.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ProgressIndexProvider>
          <App />
        </ProgressIndexProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
