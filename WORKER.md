# Research worker — extra steps

The scheduled research task reads this file on every run and follows it in
addition to its own instructions. Keep it short and plain.

## Travel to the girls' schools (every new or re-researched unit)

The app shows estimated weekday-morning trips from each home to the places in
Firestore `hs_meta/places` (currently Woodleigh MRT and PLMGS on Lorong Ah Soo).

For every unit you add (and any unit missing `lat`/`transit`):

1. Find the condo's coordinates with OneMap through WebFetch (curl is blocked):
   `https://www.onemap.gov.sg/api/common/elastic/search?searchVal=<CONDO NAME or block + street>&returnGeom=Y&getAddrDetails=Y&pageNum=1`
   Pick the result matching the listing's block/street; if the development has
   several blocks, average them. Check it lands in the right neighbourhood.
2. Run, from the repo root:
   `python3 tools/transit.py unit <unitId> <lat> <lng>`
   This saves `lat`, `lng` and `transit` on the unit (bus data downloads itself
   on first use).

Do not write `transit` by hand, and do not change `hs_meta/places`.

## Fields the app owns
Also never change `nope`, `prevStatus` or `nopeRejected` (thumbs-down votes), or `seenBy`
(who has opened each home).
A unit with `nopeRejected: true` was turned down by both of them: never re-add
that listing in a rescan.

## New and Updated badges
- New units: set `isNew: true` (each person's "New" badge clears when they open it).
- When a refresh finds a real change on an existing unit (asking price, listing
  state such as "Possibly sold", or a corrected key fact), also set
  `updatedAt` to the current UTC time (`YYYY-MM-DDTHH:MM:SSZ`) and `updateNote`
  to one short plain sentence, e.g. "Asking down from S$2.88M to S$2.75M".
  Don't set them when nothing meaningful changed (e.g. only checkedAt).

## School runs are the deciding rule (18 Oct 2026)
Everything the research finds or suggests on its own (rescans, "more like X"
ideas, notes recommending other homes) must have a PLMGS run of "easy" or "ok"
in `tools/transit.py`. Never add, suggest or argue for a home with a "hard"
school run, however good it looks otherwise — condo or landed.
Homes Adrian or Shernice paste themselves are their deliberate choice: they
add these when a home might be worth a bigger change in lifestyle and school
logistics. Always add them, tag the school run under `concerns` (e.g. "School
runs hard (PLMGS ~59 min)"), and don't push back or recommend against them in
notes. Agent suggestions follow the same rule as pasted links.

## Refined criteria (from their ratings, 17 Oct 2026)
These sharpen the criteria in your instructions. For **rescans**, only add homes
that meet all of them. If you are reading this after a rescan, re-check every
unit you added this run against them and delete any that miss (they are new,
unrated and uncommented, so nothing of theirs is lost). For **links they paste**, always add the home, but list
any of these it misses under `concerns` (short tags such as "Under 1,400 sqft").

1. **Size:** at least about 1,400 sqft, with decent bedroom sizes. Units around
   1,200–1,300 sqft were rejected as "too small" / "bedrooms too small".
2. **School run to PLMGS (Lorong Ah Soo) must be "easy" or "ok"** in
   `tools/transit.py` (not "hard"). In practice: Kovan, Hougang, Serangoon,
   Bartley, Upper Serangoon, out to about Buangkok. Skip Sengkang West, Punggol
   and Fernvale — they were consistently rejected as too far.
   Run `python3 tools/transit.py point <lat> <lng>` before adding a rescan find.
3. **Development:** mid-to-large condos with full facilities and good upkeep.
   Skip boutique blocks (under ~100 units) and tired-looking older projects,
   even if freehold or very near Kovan.
4. **Ground-floor privacy:** for GF units, prefer a private, screened patio.
   Flag pool-facing or open patios as a concern ("Pool-facing patio").
5. **More like Riverfront Residences** (large, newer, ~1,400–1,500 sqft 4BR,
   high floor with greenery) — the development they both like most.

Format (GF / penthouse / high floor / townhouse) is not a deciding factor, and
freehold is not a plus on its own. Budget, lease and 6 km rules are unchanged,
except for landed homes below.

## Lease exception for penthouses near an MRT (18 Oct 2026)
The usual rule is at least 80 years of lease left. For **penthouses within
about 600 m (≈8-min walk) of an MRT station**, accept **70 years or more**.
Note the lease under `concerns` when it is below 80 (e.g. "Lease ~73 yrs").
All other rules (budget, school runs, size, 6 km) still apply.

## Landed homes (added 17 Oct 2026)
Landed homes are now in scope too: cluster houses, strata terraces, townhouses
and other landed homes within 6 km of Kovan.
- **Budget:** up to about **S$3.0M** for landed (condos stay at S$2.8M).
- **Set `landed: true`** on every landed unit you add — the app then uses the
  S$3.0M budget for it. Don't add an "Over budget" concern below S$3.0M.
- **School runs still apply:** PLMGS must be "easy" or "ok" in
  `tools/transit.py`, same as condos. This rules out most of Seletar Hills
  (Sunrise Terrace etc. came out "hard"); look in Kovan, Hougang, Serangoon
  Gardens/Chartwell, Upper Serangoon and Bartley first.
- **Size/layout:** at least 4 bedrooms, or 3 plus a study/guest room that can
  serve as a bedroom; ~2,000 sqft or more is typical and fine.
- The "mid-to-large condo" rule doesn't apply to landed, but for cluster homes
  note facilities and upkeep in `notes`; flag very old or tired houses as a concern.

## Duplicates and repeats
- **Same unit, different agent:** before adding any listing, compare it with
  existing units of the same development. If size matches and the floor/stack,
  view or facing match (or the price is within ~3% with nothing contradicting),
  treat it as the SAME unit: do not create a new unit. Instead append
  `{"url": ..., "askingM": ...}` to that unit's `otherListings` array and
  mention it in the run summary. If unsure, add it and set
  `dupOf: {"id": <existing unit id>, "label": "<short reason>"}` — the app then
  asks them "Same unit / Different unit" on the new card. Never set `dupOf` on a
  unit that has `dupChecked: true` (they already said it's different).
- **Links they merged:** Firestore `hs_meta/merged` has `urls`, the listings they
  marked as the same unit in the app. Never add a listing whose URL is in that
  list or already in any unit's `otherListings` (compare without query strings).
  This applies to rescans; a link they paste again is still added.
- **Refreshing prices:** also re-check each `otherListings` entry's asking price
  and update its `askingM`; if another agent's price is lower than the unit's
  `askingM`, say so in `updateNote` (e.g. "Also listed at S$2.35M by another agent").
- **Variety in rescans:** "More like Riverfront Residences" means similar
  developments, not more Riverfront units. Add at most 2 new listings from any
  one development per rescan, and only if they're clearly different units
  (different size, or clearly different floor/stack).
- A pasted link to a development they rejected before is still added (they
  chose it), with a concern tag noting the earlier rejection.

## Suggestions from the agent
Requests with `suggestedBy` (e.g. "Andrew") came from their agent's board.
Treat them like pasted links (always add, tag misses under `concerns`), and
start the unit's `notes` with "Suggested by Andrew" plus his `note` if any.

## Where a new home came from
On every unit you create, also set:
- `addedAt`: current UTC time (`YYYY-MM-DDTHH:MM:SSZ`)
- `source`: "scan" (rescan find), "link" (a pasted link) or "agent" (request has `suggestedBy`)
- `addedBy`: the request's `by` ("adrian" / "shernice") for pasted links
The app uses these for its "New for you to review" list (newest first, with "From Claude's scan" / "Added by Shernice" / "Suggested by Andrew").

## Listing photo
For every unit you add (or any active unit missing `photoUrl`), set `photoUrl` to a photo
of the UNIT itself. On PropertyGuru, list the gallery photos with their alt-text labels
and pick, in order of preference: Living Room → Dining → Balcony/Patio/View → Bedroom →
Kitchen/Study. Only use URLs under /listing/<thatListingId>/UPHO. — never
/projectnet-project/ (developer stock images of the condo) or floor plans (ZUFP).
If the photos have no labels, use the first /listing/<id>/UPHO. photo and set
`photoNote` "Photo may not be of this unit"; if the listing says its images are AI /
artist impressions, set `photoNote` "AI-generated impression (per listing)".
If there are only development photos, leave `photoUrl` unset — the app shows a coloured tile.

## Activity feed
The app's bell shows an Activity feed read from `hs_meta` docs that have an
`actAt` field. If you ever add a comment to a unit (`hs_units/<id>/comments`),
also create `hs_meta/act_<random>` with
`{"kind":"comment","by":"claude","unitId":<id>,"unitName":<name>,"text":<first 300 chars>,"actAt":<UTC ISO>}`.
Never edit or delete other `act_*` docs or `hs_meta/actread`.
