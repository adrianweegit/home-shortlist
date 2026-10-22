# Our Kovan Home — guide for Claude

Read this first in any new thread, then `HANDOFF.md` (current state) and `WORKER.md`
(rules the research worker and Claude follow when rating homes). Adrian is not a
software person: explain in plain words, no jargon, and always **read back and
suggest enhancements before building** unless he says "proceed".

## What this is
A private home-search app for Adrian and Shernice (and their agent Andrew) at
https://adrianweegit.github.io/home-shortlist/ — one vanilla-JS PWA (`index.html`),
Andrew's board (`agent.html`), a service worker, and a Firestore database inside the
Number Bomb Firebase project. The public repo holds code only; **all listing data,
people's names, schools and comments live in Firestore**. Never add the kids' names
or schools to the repo (use the `hs_meta/places` keys `plmgs` and `woodleigh`).

## Security rules that never change
- Data stays in Firestore, never in the repo or in chat logs you create.
- The research bot signs in as `hs-bot@…` with `HS_BOT_PASSWORD`. The password is
  **only** in the scheduled task's settings and in Adrian's hands — ask him for it in a
  new thread, export it in the shell, never commit it, never write it to memory.
- School runs use OneMap's public-transport routing (real timetables) via
  `ONEMAP_EMAIL` / `ONEMAP_PASSWORD` (Adrian's free OneMap account) — same handling as
  the bot password: scheduled task settings only, ask Adrian in a new thread. Without
  them `tools/transit.py` falls back to its own estimate. `www.onemap.gov.sg` must be on
  the allowed-domains list (it is).
- Andrew's board is unauthenticated: it may only write `replies, agentNote,
  suggestions, files, replyAt, agentSeenAt` on `hs_board/{token}` and create small docs
  in `hs_board/{token}/files`. Private things (exact hearts, Claude ratings, fair
  values, target offers, budget) never go to the board.
- Firebase rules live in `firestore.rules.combined` (Number Bomb + this app). Any rules
  change: edit that file, send Adrian a `.txt` copy, he pastes it into the console.
  Don't touch the Number Bomb section.

## Layout of the code
- `index.html` — the app. Firebase compat SDK 10.14.1. Key areas: filters/sort
  (`FILTERS`, `homesFiltered`), cards (`card`), details sheet (`renderSheet`,
  `andrewBox`, `agentFilesHTML`), activity feed (`logAct`, `renderActivitySheet`),
  floor plans (`openPlan`, `uploadPlan`, `useAsPlan`), Andrew sync
  (`syncBoardFromApp` app→board, `applyBoardReplies` board→app, both REST), update
  checker (`APP_VERSION`, `checkForUpdate`). REST helpers: `restPatch`, `restCall`,
  `fsEnc/fsDec`, `fp()` (backticks odd path segments).
- `agent.html` — Andrew's board. Plain fetch to Firestore REST with the API key.
  Autosaves; sends only homes he touched over the latest board state. Preview mode
  `?preview=1` (opened from the app) never writes.
- `sw.js` — network-first cache, `cache:"no-cache"`. Bump `CACHE` name on big changes.
- `config.js` — Firebase web config, allowed emails, `budgetM` 2.8 / `landedBudgetM` 3.0.
- `tools/hs.py` — bot REST helper: `get/update/put/delete(coll, id, …)` with
  `coll` in `units|requests|meta`, `list_docs("hs_units")`, `_req(method,url,body)`,
  `enc/dec/doc_out`, `BASE`. `tools/transit.py point <lat> <lng>` / `unit <id> <lat> <lng>`
  computes school runs (bus data caches in `/tmp/hs-busdata`).
- `WORKER.md` — rules for the scheduled research worker (trigger
  `trig_01WE9DPdz9R1CUgngBYfGe6o`; fire it with `fire_trigger` + extra text).

## Firestore shape (collections)
`hs_units/{id}` (+ `comments` subcollection), `hs_requests`, `hs_meta/{agent, places,
worker, merged, actread, act_*, plan_*}`, `hs_board/{token}` (+ `files`).
Unit fields worth knowing: `status` (Unviewed/Booked/Viewed/Offer/Rejected), `appt`,
`ratings.{adrian,shernice}`, `nope`, `claude{n,why,at}`, `concerns[]`, `loves[]`,
`listingState` (Live / Sold… / Withdrawn…), `landed`, `driveSchool`, `planDoc`,
`floorPlanUrl`, `agentAsk`, `agentDrop`, `rejectReason`, `dupOf`, `otherListings`.
Board item fields: `status new|upcoming|offer|viewed|closed`, `appt`, `priority`,
`rank`, `ask`, `spec`, `thread[]`, `dropAnswer`; board-level `wants`, `free`, `busy`,
`slotAsk`, `files[]`, `replies`, `appliedReplies`, `appliedSuggestions`, `appliedFiles`.

## How to work
1. **Bot writes:** `export HS_BOT_PASSWORD=…` then `python3 - <<'E' … import hs … E`
   from the repo root. Prefer small targeted updates; never overwrite user-owned
   fields (`ratings`, `nope`, `seenBy`, comments, `concerns` you didn't add).
2. **Test before publishing.** Playwright is set up in `/tmp/t` (may be gone in a new
   session — recreate: copy `index.html`, strip the gstatic script tags, insert
   `<script src="stub.js">` after `config.js`; a stub fakes `window.firebase`). For
   `agent.html`, route `firestore.googleapis.com/**` to a saved board JSON.
   Always `node --check` the extracted script before pushing.
3. **Publish:** bump `APP_VERSION` (`python3 tools/bump.py` or edit the line — keep the
   regex on the next lines intact!), then
   `git add … && git commit && git push -q origin main main:gh-pages`. Commits use
   author "Adrian Wee <adrian.wee79@gmail.com>" plus the Claude trailer. Then poll
   `gh api repos/adrianweegit/home-shortlist/actions/runs?per_page=1` until
   `completed success` (GitHub can take 1–40 min). The app shows a "New version" bar.
4. **Research replies** end with a Sources list. WebFetch needs provenance: only URLs
   the user pasted or that appeared in a search/fetch result. PropertyGuru listing pages
   can be stale cached copies — confirm a "back on market" against the development's
   search-results page before reviving a sold/withdrawn unit.
5. **Andrew's messages** (viewing times, "sold", drops) can be applied by hand via the
   bot if his board hasn't synced; keep `replies`, `appliedReplies` and `items` in step.

## Style Adrian expects
Short, plain, structured replies; tables for comparisons; honest about what was and
wasn't tested; one next step at the end. Readback-then-build for any UI change.
