const { test, expect } = require("@playwright/test");
test("analyst runs a labeled company model and invalidates stale assumptions", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Explore DEMO DATA" }).click();
  await expect(
    page.getByText("DEMO DATA — Meridian Tools", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Cash behind earnings", { exact: true }),
  ).toBeVisible();
  await expect(page.locator("#empty")).toBeHidden();
  await expect(
    page.getByText("Structured filing facts", { exact: true }),
  ).toBeVisible();
  await page.getByLabel("Normalized tax rate (%)").fill("30");
  await expect(
    page.getByText("Cash behind earnings", { exact: true }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Analyze statements" }).click();
  await expect(
    page.getByText("Cash behind earnings", { exact: true }),
  ).toBeVisible();
});
test("charts reconcile comparable statements and cash movements", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Explore DEMO DATA" }).click();
  await expect(
    page.getByRole("img", {
      name: "Revenue and operating cash flow by fiscal period",
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "Opening to closing cash reconciliation" }),
  ).toBeVisible();
  await expect(
    page.getByText("Net income → operating cash flow", { exact: true }),
  ).toBeVisible();
});
test("offline imports and evidence exports recalculate; bad files clear output", async ({
  page,
  request,
}, testInfo) => {
  const demo = await (await request.get("/api/demo")).json();
  await page.goto("/");
  await page.locator("#file").setInputFiles({
    name: "companyfacts.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(demo.companyfacts)),
  });
  await page.getByRole("button", { name: "Analyze statements" }).click();
  await expect(
    page.getByText("USER PROVIDED DATA", { exact: true }),
  ).toBeVisible();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export evidence package" }).click();
  const download = await downloadPromise;
  const exported = testInfo.outputPath("evidence.json");
  await download.saveAs(exported);
  await page.locator("#file").setInputFiles(exported);
  await page.getByRole("button", { name: "Analyze statements" }).click();
  await expect(
    page.getByText("Cash behind earnings", { exact: true }),
  ).toBeVisible();
  await page.locator("#file").setInputFiles({
    name: "bad.json",
    mimeType: "application/json",
    buffer: Buffer.from("{bad"),
  });
  await expect(page.locator("#error")).not.toBeEmpty();
  await expect(
    page.getByText("Cash behind earnings", { exact: true }),
  ).toHaveCount(0);
});

test("responsive evidence remains readable and imported text does not execute", async ({
  page,
  request,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Explore DEMO DATA" }).click();
  await expect(
    page.getByRole("img", { name: "Opening to closing cash reconciliation" }),
  ).toBeVisible();
  await page.screenshot({
    path: "docs/assets/workbench-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator("body")).toHaveJSProperty("scrollWidth", 390);
  await page.screenshot({
    path: "docs/assets/workbench-mobile.png",
    fullPage: true,
  });
  const demo = await (await request.get("/api/demo")).json();
  demo.companyfacts.entityName = '<img src=x onerror="window.executed=true">';
  await page.locator("#file").setInputFiles({
    name: "issuer.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(demo.companyfacts)),
  });
  await page.getByRole("button", { name: "Analyze statements" }).click();
  await expect(
    page.getByText(demo.companyfacts.entityName, { exact: true }),
  ).toBeVisible();
  expect(await page.evaluate(() => window.executed)).toBeUndefined();
});

test("SEC retrieval provenance survives export and is unverified on reimport", async ({
  page,
  request,
}, testInfo) => {
  const demo = await (await request.get("/api/demo")).json();
  const metadata = {
    raw_sha256: "a".repeat(64),
    retrieved_at: "2026-09-08T00:00:00Z",
    url: "https://data.sec.gov/api/xbrl/companyfacts/CIK0000001234.json",
  };
  await page.route("**/api/fetch", (route) =>
    route.fulfill({ json: { companyfacts: demo.companyfacts, metadata } }),
  );
  await page.goto("/");
  await page.getByText("Retrieve from SEC EDGAR", { exact: true }).click();
  await page.locator("#cik").fill("1234");
  await page.locator("#contact").fill("LedgerLens analyst@example.org");
  await page.locator("#fetch").click();
  await page.locator("#analyze").click();
  const save = async (name) => {
    const pending = page.waitForEvent("download");
    await page.getByRole("button", { name: "Export evidence package" }).click();
    const file = testInfo.outputPath(name);
    await (await pending).saveAs(file);
    return [file, JSON.parse(require("node:fs").readFileSync(file, "utf8"))];
  };
  const [file, first] = await save("sec.json");
  expect(first.source_metadata.observation).toEqual(metadata);
  expect(first.source_metadata.origin).toBe("SEC retrieval in this session");
  await page.locator("#file").setInputFiles(file);
  await page.locator("#analyze").click();
  const [, restored] = await save("restored.json");
  expect(restored.source_metadata.observation).toEqual(metadata);
  expect(restored.source_metadata.origin).toBe(
    "Supplied provenance; not verified",
  );
  expect(restored.input.source_label).toBe("USER PROVIDED DATA");
});
