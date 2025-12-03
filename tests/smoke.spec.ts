import { test, expect } from "@playwright/test";

test.describe("Audio Sentiment Bot", () => {
  test("exposes plug-and-play instrument workflow", async ({ page }) => {
    await page.goto("/");

    await expect(page.locator("h1.brand__title")).toHaveText("Audio Sentiment Bot");
    await expect(page.locator(".brand__subtitle")).toContainText("Plug in an electric guitar");

    const instrumentSelect = page.locator("[data-instrument-mode]");
    await expect(instrumentSelect).toBeVisible();

    const instrumentStatus = page.locator("[data-instrument-status]");
    await instrumentSelect.selectOption("instrument");
    await expect(instrumentStatus).toContainText("Instrument mode");
    await instrumentSelect.selectOption("voice");
    await expect(instrumentStatus).toContainText("Voice mode");

    const quickstart = page.locator(".instrument-quickstart__steps li");
    await expect(quickstart).toHaveCount(3);

    await expect(page.locator("[data-live-card]")).toHaveAttribute("hidden", "");
    await expect(page.locator("[data-live-trend]")).toBeAttached();

    const ciStatus = page.locator("[data-ci-status]");
    await expect(ciStatus).toBeVisible();
    const ciText = (await ciStatus.textContent())?.trim() || "";
    expect(ciText.length).toBeGreaterThan(0);
  });
});
