/*
 * JobPilot — capture d'annonce.
 *
 * Reads the description of the job posting the user is looking at and sends it
 * to the JobPilot running on this machine, so the CV is tailored against the
 * real posting instead of the ~113-character card an alert email carries.
 *
 * WHAT THIS DOES NOT DO, deliberately and permanently:
 *   - it never navigates, opens a tab, or follows a link;
 *   - it never fetches a page, including the one it is on;
 *   - it never runs on a page the user did not open themselves;
 *   - it never acts on anything but the page currently in front of them.
 * There is no background service worker and no scheduled work. That is the
 * line between this and scraping — see CLAUDE.md, "Scope of rule 11".
 *
 * It is also invisible when JobPilot is not running: a failed request produces
 * no toast, no error and no output of its own. (Chrome itself logs a refused
 * connection in the console; that line comes from the browser's network stack,
 * not from this file, and cannot be suppressed from a content script.)
 */

(() => {
  "use strict";

  const ENDPOINT = "http://127.0.0.1:8787/offer/import";

  /* -------------------------------------------------------------------- *
   * SELECTORS — THE PART THAT ROTS
   *
   * These are the only site-specific knowledge in the extension, and they are
   * guaranteed to break: all three sites ship obfuscated, generated class
   * names and change them without notice. When capture stops working on one
   * site, this table is the first and usually the only thing to edit.
   *
   * A miss is not a failure. Every entry is tried in order and the first one
   * with enough text wins; if none matches, largestTextBlock() below takes
   * over, which knows nothing about any site and therefore cannot rot.
   * -------------------------------------------------------------------- */
  const SELECTORS = {
    "linkedin.com": [
      // The panel on the right of the jobs search, and the standalone page.
      ".jobs-description__content",
      ".jobs-box__html-content",
      "#job-details",
      ".jobs-description-content__text",
      // Logged-out / public posting view.
      ".show-more-less-html__markup",
      ".description__text",
    ],
    "indeed.fr": [
      "#jobDescriptionText",
      ".jobsearch-JobComponent-description",
      '[data-testid="jobsearch-JobComponent-description"]',
    ],
    "welcometothejungle.com": [
      '[data-testid="job-section-description"]',
      '[data-testid="job-sections"]',
      "div[class*='sc-'] section",
      "article",
    ],
  };

  /* Minimum accepted length, mirroring MIN_IMPORTED_DESCRIPTION_CHARS in
   * src/jobpilot/offer_import.py. Checked here too so a nav bar or a cookie
   * banner is never even sent. The server is the authority; this is politeness.
   */
  const MIN_CHARS = 200;

  /* How long to wait for the page the user opened to finish rendering. All
   * three sites load the description after the shell. Bounded, then silence.
   */
  const POLL_MS = 400;
  const POLL_LIMIT = 15; // ~6 seconds

  /* Containers that are never the posting. */
  const CHROME_TAGS = new Set(["NAV", "HEADER", "FOOTER", "ASIDE", "FORM"]);

  const sent = new Set();

  function hostKey() {
    const host = location.hostname.toLowerCase();
    return Object.keys(SELECTORS).find(
      (key) => host === key || host.endsWith("." + key)
    );
  }

  function textOf(element) {
    if (!element) return "";
    // innerText, not textContent: it respects display:none and line breaks, so
    // hidden "show more" duplicates and inline scripts do not come along.
    return (element.innerText || "").trim();
  }

  function fromSelectors(key) {
    for (const selector of SELECTORS[key] || []) {
      let nodes;
      try {
        nodes = document.querySelectorAll(selector);
      } catch (error) {
        continue; // a malformed selector must not take the whole capture down
      }
      for (const node of nodes) {
        const text = textOf(node);
        if (text.length >= MIN_CHARS) return text;
      }
    }
    return "";
  }

  /* The fallback: the tightest element that still holds most of the page's
   * text. Site-agnostic on purpose — it is what keeps a rotted selector from
   * turning into a broken feature.
   */
  function largestTextBlock() {
    const candidates = [];
    for (const node of document.querySelectorAll("article, main, section, div")) {
      if (node.closest("nav, header, footer, aside")) continue;
      if (CHROME_TAGS.has(node.tagName)) continue;
      const length = textOf(node).length;
      if (length >= MIN_CHARS) candidates.push({ node, length });
    }
    if (!candidates.length) return "";

    candidates.sort((a, b) => b.length - a.length);
    let best = candidates[0];
    // Descend while a child still carries almost all of the parent's text: the
    // biggest element is usually a wrapper holding the whole page.
    let moved = true;
    while (moved) {
      moved = false;
      for (const candidate of candidates) {
        if (
          candidate.node !== best.node &&
          best.node.contains(candidate.node) &&
          candidate.length >= best.length * 0.9
        ) {
          best = candidate;
          moved = true;
          break;
        }
      }
    }
    return textOf(best.node);
  }

  function describe() {
    const key = hostKey();
    if (!key) return "";
    return fromSelectors(key) || largestTextBlock();
  }

  function toast(message) {
    try {
      const box = document.createElement("div");
      box.textContent = message;
      box.setAttribute("role", "status");
      Object.assign(box.style, {
        position: "fixed",
        bottom: "20px",
        right: "20px",
        zIndex: "2147483647",
        padding: "10px 14px",
        borderRadius: "8px",
        background: "#12161f",
        color: "#e8edf7",
        font: "13px/1.4 -apple-system, Segoe UI, Roboto, sans-serif",
        boxShadow: "0 6px 24px rgba(0,0,0,.35)",
        pointerEvents: "none",
        opacity: "0",
        transition: "opacity .18s ease",
      });
      document.body.appendChild(box);
      requestAnimationFrame(() => {
        box.style.opacity = "1";
      });
      setTimeout(() => {
        box.style.opacity = "0";
        setTimeout(() => box.remove(), 250);
      }, 2600);
    } catch (error) {
      /* A toast that fails is not worth telling anyone about. */
    }
  }

  function send(description) {
    const url = location.href;
    if (sent.has(url)) return;
    sent.add(url);

    fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url,
        description,
        title: (document.title || "").trim(),
      }),
    })
      .then((response) => {
        if (!response.ok) {
          // A refusal is the server's business, not the user's. The commonest
          // one is "description trop courte", which means the page had not
          // finished rendering — allow a later attempt on this URL.
          sent.delete(url);
          return null;
        }
        return response.json().catch(() => null);
      })
      .then((body) => {
        if (!body) return;
        const chars = body.imported_chars || description.length;
        toast(
          body.created
            ? `JobPilot : nouvelle offre importée (${chars} caractères)`
            : `JobPilot : description importée (${chars} caractères)`
        );
      })
      .catch(() => {
        // JobPilot is not running. That is the normal state of this machine
        // most of the time and is not an error worth showing anyone.
        sent.delete(url);
      });
  }

  function attempt(remaining) {
    let description = "";
    try {
      description = describe();
    } catch (error) {
      description = "";
    }
    if (description.length >= MIN_CHARS) {
      send(description);
      return;
    }
    if (remaining > 0) {
      setTimeout(() => attempt(remaining - 1), POLL_MS);
    }
    // Otherwise: give up, silently. The paste box on the JobPilot detail page
    // is the other half of this feature and is always available.
  }

  /* All three sites are single-page apps: clicking a job changes the URL
   * without a reload, so a load-only hook would fire on the first posting and
   * never again. This reacts to the user's own navigation and nothing else —
   * it does not cause navigation, and it looks at no page but the current one.
   */
  let lastUrl = location.href;
  function watchNavigation() {
    setInterval(() => {
      if (location.href !== lastUrl) {
        lastUrl = location.href;
        attempt(POLL_LIMIT);
      }
    }, 1000);
  }

  /* The browser runs this file for its side effects. Under CommonJS — which is
   * how tests/test_extension.py exercises the extraction against a stub DOM —
   * it must export its helpers and start NOTHING: watchNavigation() sets an
   * interval, and an interval keeps node alive forever.
   *
   * `module` is undefined in a content script, so the browser always takes the
   * else branch and the export is dead code there.
   */
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { SELECTORS, MIN_CHARS, describe, largestTextBlock, hostKey };
  } else {
    attempt(POLL_LIMIT);
    watchNavigation();
  }
})();
