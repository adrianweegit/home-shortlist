# Handoff — current state (update this at the end of every working session)

_Last updated: 21 Oct 2026 by Claude (thread "Our Kovan Home", session
01TR8szLVGUBomMmR9xRpemz)._

## Where things stand
- **46+ active homes** in the app; budget S$2.8M condo / S$3.0M landed; within 6 km of
  Kovan; school runs are the deciding rule (see WORKER.md), except homes with
  `driveSchool: true` (Grande Vista, Cabana x5, Alana) where Adrian will drive the
  younger child to school daily — don't cap their rating for school runs.
- **Top of mind (Andrew's board):** Heron Bay (dual-key PH, S$2.88M ask, target
  S$2.55–2.6M, needs major reno), NIN Residence PH (likely 83 Pheng Geck Ave #19-02,
  viewing **Sat 25 Oct 3:00 pm**, roof structure unapproved, ask for caveat), Bartley
  Residences GF, The Garden Residences PH, Riverfront 1485 (viewed — no indoor dining).
- **Viewed 18 Oct:** Stars of Kovan (rejected), The Minton G1 (level 2, no privacy),
  Riverfront 1485 (great view, cramped). The Minton 6A (Blk 6A) rejected 19 Oct —
  really 2BR+study.
- **Riversails:** both 4BR units gone (500271127 sold per Andrew; 500240802 corner
  withdrawn — worker must not revive it). Penthouse 500218291 still live, plan added.
- **Cabana (Seletar Hills, 103-yr cluster houses):** 70 ads for 119 houses; Far East
  fixed at S$1,080 psf; owners resell 5–13% below. Best: #187 (2,917 sqft, renovated,
  S$2.75M, 3 hearts) and #145A (3,046 sqft, renovated, S$2.88M, 3 hearts). #205
  (unrenovated S$2.90M) and the two S$2.95–3.0M ones are weaker.
- **Grande Vista** (Cactus Drive, 999-yr, 2,024 sqft maisonette, S$2.62M, offer already
  in): 4 hearts; viewing not yet booked; Adrian drives for school.
- **Jewel @ Buangkok GF dual-key** (1,647 sqft, S$2.88M): waiting on Andrew for floor
  plan, stack/unit number (ground-floor + PES to be confirmed), seller flexibility.

## Features shipped (all live)
Activity feed + bell + app-icon badge · Claude's rating (green hearts, not in Top 5) ·
"With Andrew" box per home (ask line, conversation, his files, drop suggestions) ·
Our chat stays private ("↗ Send to Andrew" per message) · floor plans: upload ours,
view/zoom, "Use as floor plan" for Andrew's files (images + PDF) · Andrew's board:
autosave, size line, thread, reply box, 📎 attach files, 🗑️ drop with reason, Sold/
Confirmed/Checking, free-time row, "What's top of mind", "What we're looking for" ·
Homes tab: "🤝 With Andrew" filter + "On Andrew's board first" sort + board status
line on cards · sold/withdrawn homes drop out of Top 5 with "It's still available" undo ·
update bar + version footer · details page doesn't redraw while a field is being edited.

## Open items / ideas not yet built
- UI clean-ups still on the list: quieter Top-of-mind list on the board, Blk/stack in
  names for the two Mintons and Riversails, collapse Closed section, hide empty
  Claude's notes, chat shortcut in the sheet header, softer concern chips, one "New"
  marker per card, driving time to school on `driveSchool` cards.
- Worker should start reading Andrew's PDF floor plans (instruction is in WORKER.md;
  not yet observed working).
- Fair value for NIN PH is low confidence — needs the caveat from Andrew.

## Gotchas learned
- A board page left open on Andrew's phone used to resend old state (fixed: only
  touched homes are sent). If a time reverts, check `hs_board.replies` vs `items`.
- `sed` version bumps once clobbered the `APP_VERSION` regex — use `bump.py` or edit
  by hand and `node --check`.
- GitHub Pages can queue deploys for 30+ min; older queued runs get cancelled by the
  newest one, which is normal.
- Firestore docs are capped at 1 MB: uploaded plans/files are kept under ~730 KB.
