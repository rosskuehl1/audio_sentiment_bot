"use strict";

(function () {
  const form = document.querySelector("[data-form]");
  if (!form) {
    return;
  }

  const fileInput = form.querySelector('[data-input="audio"]');
  const languageSelect = form.querySelector('[data-input="language"]');
  const submitButton = form.querySelector('[data-submit]');
  const statusEl = document.querySelector('[data-status]');
  const resultsEl = document.querySelector('[data-results]');
  const emptyStateEl = document.querySelector('[data-empty-state]');

  if (!fileInput) {
    return;
  }

  const setStatus = (message, state) => {
    const tone = state || "ready";
    if (statusEl) {
      statusEl.textContent = message;
      statusEl.dataset.state = tone;
    }
  };

  const toggleLoading = (isLoading) => {
    if (submitButton) {
      submitButton.disabled = Boolean(isLoading);
    }
    form.classList.toggle("is-uploading", Boolean(isLoading));
  };

  const ensureEmptyState = () => {
    if (!emptyStateEl) {
      return;
    }
    const hasResults = resultsEl && resultsEl.childElementCount > 0;
    emptyStateEl.hidden = Boolean(hasResults);
  };

  const formatScore = (value) => {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return "--";
    }
    return value.toFixed(2);
  };

  const toneFromLabel = (label) => {
    switch (label) {
      case "POSITIVE":
        return "positive";
      case "NEGATIVE":
        return "negative";
      case "NEUTRAL":
        return "neutral";
      default:
        return "unknown";
    }
  };

  const buildResultCard = (payload) => {
    const sentiment = payload && payload.sentiment ? payload.sentiment : null;
    const label = sentiment && sentiment.label ? sentiment.label : "UNKNOWN";
    const score = sentiment && sentiment.score != null ? sentiment.score : null;
    const transcript = payload && typeof payload.transcript === "string" ? payload.transcript : "";
    const language = payload && payload.language ? payload.language : "en-US";
    const note = payload && payload.error ? payload.error : "";
    const fileName = payload && payload.fileName ? payload.fileName : "Audio clip";
    const tone = toneFromLabel(label);

    const article = document.createElement("article");
    article.className = "result-card";
    article.dataset.tone = tone;
    article.tabIndex = -1;

    const header = document.createElement("div");
    header.className = "result-card__header";

    const title = document.createElement("h3");
    title.className = "result-card__title";
    title.textContent = label === "UNKNOWN" ? "No sentiment detected" : label;
    header.appendChild(title);

    const badge = document.createElement("span");
    badge.className = "badge";
    badge.dataset.tone = tone;
    badge.textContent = label === "UNKNOWN" ? "--" : label + " | " + formatScore(score);
    header.appendChild(badge);

    article.appendChild(header);

    const meta = document.createElement("p");
    meta.className = "result-card__meta";
    const now = new Date();
    const formattedTime = now.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    meta.textContent = fileName + " | " + language + " | " + formattedTime;
    article.appendChild(meta);

    const transcriptBlock = document.createElement("p");
    transcriptBlock.className = "result-card__transcript";
    transcriptBlock.textContent = transcript ? transcript : "No speech detected.";
    article.appendChild(transcriptBlock);

    if (note && tone === "unknown") {
      const noteBlock = document.createElement("p");
      noteBlock.className = "result-card__note";
      noteBlock.textContent = note;
      article.appendChild(noteBlock);
    }

    requestAnimationFrame(() => {
      try {
        article.focus();
      } catch (_focusError) {
        /* ignore focus failures */
      }
      article.addEventListener(
        "blur",
        () => {
          article.removeAttribute("tabindex");
        },
        { once: true }
      );
    });

    return article;
  };

  const resetFileInput = () => {
    const preservedLanguage = languageSelect ? languageSelect.value : "en-US";
    form.reset();
    if (languageSelect) {
      languageSelect.value = preservedLanguage;
    }
  };

  const handleError = (err) => {
    const message = err instanceof Error ? err.message : "Request failed.";
    setStatus(message, "error");
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!fileInput.files || fileInput.files.length === 0) {
      setStatus("Select an audio file to begin.", "error");
      fileInput.focus();
      return;
    }

    const audioFile = fileInput.files[0];
    const language = (languageSelect && languageSelect.value) || "en-US";

    const formData = new FormData();
    formData.append("audio", audioFile);
    formData.append("language", language);

    setStatus("Analyzing audio...", "working");
    toggleLoading(true);

    try {
      const response = await fetch("/analyze", {
        method: "POST",
        body: formData,
      });

      let payload = {};
      try {
        payload = await response.json();
      } catch (jsonError) {
        throw new Error("Unexpected server response.");
      }

      if (!response.ok) {
        throw new Error(payload && payload.error ? payload.error : "Request failed.");
      }

      payload.fileName = audioFile.name;

      if (resultsEl) {
        const resultCard = buildResultCard(payload);
        resultsEl.prepend(resultCard);
      }
      ensureEmptyState();

      if (payload.error && !payload.sentiment) {
        setStatus(payload.error, "warn");
      } else {
        setStatus("Analysis complete.");
      }
    } catch (err) {
      handleError(err);
    } finally {
      toggleLoading(false);
      resetFileInput();
    }
  });

  ensureEmptyState();
})();
