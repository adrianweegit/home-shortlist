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
