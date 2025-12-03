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

  test("restores and clears persisted history", async ({ page }) => {
    const storedEntries = [
      {
        transcript: "Stored riff feels uplifting",
        sentiment: { label: "POSITIVE", score: 0.91 },
        fileName: "Stored clip",
        timestamp: "2025-01-01T12:00:00.000Z",
        error: "",
      },
    ];
    await page.addInitScript((entries) => {
      window.localStorage.setItem("audio-sentiment-history", JSON.stringify(entries));
    }, storedEntries);

    await page.goto("/");

    const historyCards = page.locator(".result-card");
    await expect(historyCards).toHaveCount(storedEntries.length);
    await expect(historyCards.first()).toContainText("Stored clip");

    const clearButton = page.locator("[data-clear-history]");
    await expect(clearButton).toBeEnabled();
    await clearButton.click();

    await expect(historyCards).toHaveCount(0);
    await expect(page.locator("[data-empty-state]")).toBeVisible();
    await expect(clearButton).toBeDisabled();
  });
});
