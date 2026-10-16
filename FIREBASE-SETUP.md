# Firebase setup — Our Kovan Home

The app reuses the **number-bomb-a166b** Firebase project. It only adds new
collections (`hs_units`, `hs_requests`, `hs_meta`) and leaves Number Bomb's
rooms untouched.

## 1. Sign-in providers
Firebase console → **Authentication → Sign-in method**
- **Google** → Enable (support email: adrian.wee79@gmail.com) → Save.
- **Email/Password** → Enable → Save. (Only used by the research bot.)

## 2. Authorised domain
Authentication → **Settings → Authorized domains** → Add `adrianweegit.github.io`
(skip if already there from Number Bomb).

## 3. Security rules
Firestore Database → **Rules** → replace everything with the contents of
[`firestore.rules.combined`](firestore.rules.combined) → **Publish**.

That file is Number Bomb's current rules, unchanged, plus one block before the
final catch-all that lets only these accounts touch the `hs_*` collections:
- adrian.wee79@gmail.com and meiyi77@gmail.com (Google, verified email)
- hs-bot@number-bomb-a166b.firebaseapp.com (the research bot)

If Number Bomb's rules change later, copy the `Home Shortlist` block across again.

## 4. Research bot
Claude creates the bot account itself once Email/Password is enabled, and keeps
its password in the scheduled task's settings — never in this repo.

## Notes
- The Firebase web config in `config.js` is a public identifier, not a secret.
  The rules above are what keep the data private.
- iPhone: open the site in Safari → Share → **Add to Home Screen**, then sign
  in from the home-screen app itself (it keeps its own sign-in).
