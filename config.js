// Home Shortlist — public configuration.
//
// The Firebase web config is a public identifier, not a secret (it ships to
// every browser). What protects the data is the Firestore rules in
// FIREBASE-SETUP.md, which only let the two people below — and the research
// bot — read or write the hs_* collections.
window.HOME_SHORTLIST = {
  firebase: {
    apiKey: "AIzaSyDcR6yulGrisupTJN0d-rLt2sXwRGfb8Wo",
    authDomain: "number-bomb-a166b.firebaseapp.com",
    projectId: "number-bomb-a166b",
    storageBucket: "number-bomb-a166b.firebasestorage.app",
    messagingSenderId: "226121513581",
    appId: "1:226121513581:web:15eedd6db563fee2455d64"
  },
  people: {
    "adrian.wee79@gmail.com": { key: "adrian", name: "Adrian" },
    "meiyi77@gmail.com": { key: "shernice", name: "Shernice" }
  },
  budgetM: 2.8,
  landedBudgetM: 3.0,   // cluster / terrace / landed homes
  minLeaseYears: 80,
  maxKmFromKovan: 6
};
