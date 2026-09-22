import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  use: { baseURL: "http://127.0.0.1:3120", trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    { command: "../.venv/bin/python -m uvicorn tests.overview_app:app --app-dir ../backend --port 8120", url: "http://127.0.0.1:8120/health", reuseExistingServer: false },
    { command: "npm run start -- --hostname 127.0.0.1 --port 3120", env: { API_BASE_URL: "http://127.0.0.1:8120" }, url: "http://127.0.0.1:3120", reuseExistingServer: false },
  ],
});
