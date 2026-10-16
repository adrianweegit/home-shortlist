# Our Kovan Home

A small home-screen app for Adrian and Shernice to shortlist homes within 6 km
of Kovan MRT: hearts from both of us, a shared Top 5, viewings, loves and
concerns, comments, and a "+" to send listing links to Claude for research.

- `index.html` — the whole app (vanilla JS, Firebase compat SDK)
- `config.js` — Firebase web config and who can sign in
- `sw.js`, `manifest.webmanifest`, icons — add-to-home-screen support
- `tools/hs.py` — Firestore REST helper the research bot uses
- `FIREBASE-SETUP.md` — one-time console steps and rules

Live at https://adrianweegit.github.io/home-shortlist/
Listing data lives in Firestore, not in this public repo.
