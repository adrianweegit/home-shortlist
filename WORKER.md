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
