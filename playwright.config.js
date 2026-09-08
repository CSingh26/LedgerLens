const { defineConfig } = require("@playwright/test");
module.exports = defineConfig({
  testDir: "./tests/browser",
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:8195",
    channel: process.env.CI ? undefined : "chrome",
  },
  webServer: {
    command: ".venv/bin/python -m uvicorn ledgerlens.api:app --port 8195",
    url: "http://127.0.0.1:8195/health",
    reuseExistingServer: !process.env.CI,
  },
});
