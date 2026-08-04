/*
 * A DOM small enough to test the extraction and no larger.
 *
 * The extension's fallback — the site-agnostic largest-text-block heuristic —
 * is what keeps the feature alive when the per-domain selectors rot, which
 * they will. It is worth testing, and testing it needs querySelectorAll,
 * closest, innerText, tagName and contains. That is all this provides.
 *
 * Driven by tests/test_extension.py, which passes a case on argv and reads the
 * JSON verdict back. Node is used when present and the tests skip when it is
 * not, so this is never a build dependency.
 */

"use strict";

class Node {
  constructor(tag, { text = "", children = [], className = "", attrs = {} } = {}) {
    this.tagName = tag.toUpperCase();
    this.ownText = text;
    this.children = children;
    this.className = className;
    this.attrs = attrs;
    this.parent = null;
    for (const child of children) child.parent = this;
  }

  get innerText() {
    const own = this.ownText ? [this.ownText] : [];
    return own.concat(this.children.map((c) => c.innerText)).join("\n").trim();
  }

  contains(other) {
    for (let node = other; node; node = node.parent) if (node === this) return true;
    return false;
  }

  matchesOne(selector) {
    const trimmed = selector.trim();
    if (trimmed.startsWith("#")) return this.attrs.id === trimmed.slice(1);
    if (trimmed.startsWith("[")) {
      const [, name, value] = /\[([^=\]]+)="?([^"\]]*)"?\]/.exec(trimmed) || [];
      return name ? this.attrs[name] === value : false;
    }
    if (trimmed.startsWith(".")) {
      return this.className.split(/\s+/).includes(trimmed.slice(1));
    }
    return this.tagName === trimmed.toUpperCase();
  }

  matches(selector) {
    // Only the forms the harness needs: a comma list of simple selectors.
    return selector.split(",").some((part) => {
      const simple = part.trim().split(/\s+/).pop();
      return simple ? this.matchesOne(simple) : false;
    });
  }

  closest(selector) {
    for (let node = this; node; node = node.parent) {
      if (node.matches(selector)) return node;
    }
    return null;
  }

  descendants() {
    const out = [];
    const walk = (node) => {
      for (const child of node.children) {
        out.push(child);
        walk(child);
      }
    };
    walk(this);
    return out;
  }

  querySelectorAll(selector) {
    return this.descendants().filter((node) => node.matches(selector));
  }
}

const CASES = {
  // A selector hit: the per-domain table finds the description directly.
  selector_hit: () =>
    new Node("body", {
      children: [
        new Node("nav", { text: "Accueil Emplois Réseau Messagerie Notifications" }),
        new Node("div", {
          className: "jobs-description__content",
          text: "A".repeat(400),
        }),
      ],
    }),
  // The selector has rotted: the class name no longer exists anywhere, and the
  // fallback has to find the posting anyway.
  selector_rotted: () =>
    new Node("body", {
      children: [
        new Node("nav", { text: "N".repeat(300) }),
        new Node("div", {
          className: "sc-9f8e7d-obfuscated",
          children: [
            new Node("section", { text: "P".repeat(600) }),
          ],
        }),
        new Node("footer", { text: "F".repeat(300) }),
      ],
    }),
  // The whole page is chrome: nothing worth sending.
  nothing_to_find: () =>
    new Node("body", {
      children: [
        new Node("nav", { text: "N".repeat(500) }),
        new Node("footer", { text: "F".repeat(500) }),
      ],
    }),
  // A wrapper holding the posting plus a little chrome: the tightest element
  // that still carries the text is the one to send, not the outer wrapper.
  nested_wrappers: () =>
    new Node("body", {
      children: [
        new Node("div", {
          children: [
            new Node("div", {
              children: [
                new Node("article", { text: "T".repeat(800) }),
              ],
            }),
          ],
        }),
      ],
    }),
};

const [, , caseName, hostname] = process.argv;
const body = CASES[caseName]();

global.document = {
  body,
  querySelectorAll: (selector) => body.querySelectorAll(selector),
  title: "Titre de la page",
};
global.location = { hostname: hostname || "www.linkedin.com", href: "https://x.test/j/1" };
global.window = global;

const extension = require("../extension/content.js");

process.stdout.write(
  JSON.stringify({
    host_key: extension.hostKey() || null,
    described: extension.describe(),
    fallback: extension.largestTextBlock(),
    min_chars: extension.MIN_CHARS,
    domains: Object.keys(extension.SELECTORS),
  })
);
