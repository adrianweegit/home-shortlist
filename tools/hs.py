#!/usr/bin/env python3
"""Home Shortlist — Firestore REST helper for the research bot.

Signs in as the bot (email/password) and reads/writes the hs_* collections.
Credentials come from the environment, never from this repo:
    HS_BOT_EMAIL     (default hs-bot@number-bomb-a166b.firebaseapp.com)
    HS_BOT_PASSWORD  (required)

Usage:
    hs.py list units|requests|meta            -> JSON array of {id, ...fields}
    hs.py get units <id>
    hs.py set units <id> '<json>'             (replace whole doc)
    hs.py update units <id> '<json>'          (merge given top-level fields)
    hs.py delete units <id>
    hs.py add requests '<json>'               (auto id)
    hs.py comments <unitId>                   (list a unit's comments)
    hs.py import units <file.json>            (array of {id, ...} -> set each)
A JSON argument of "-" reads JSON from stdin.
"""
import json, os, sys, urllib.request, urllib.error

API_KEY = "AIzaSyDcR6yulGrisupTJN0d-rLt2sXwRGfb8Wo"
PROJECT = "number-bomb-a166b"
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents"
COLL = {"units": "hs_units", "requests": "hs_requests", "meta": "hs_meta"}
_token = None


def _req(method, url, body=None, auth=True):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    if auth:
        r.add_header("Authorization", "Bearer " + token())
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            txt = resp.read().decode()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {method} {url}\n{e.read().decode()[:800]}")


def token():
    global _token
    if _token:
        return _token
    pw = os.environ.get("HS_BOT_PASSWORD")
    if not pw:
        sys.exit("Set HS_BOT_PASSWORD")
    email = os.environ.get("HS_BOT_EMAIL", "hs-bot@number-bomb-a166b.firebaseapp.com")
    res = _req("POST", f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}",
               {"email": email, "password": pw, "returnSecureToken": True}, auth=False)
    _token = res["idToken"]
    return _token


# ---- typed value conversion -------------------------------------------------
def enc(v):
    if v is None: return {"nullValue": None}
    if isinstance(v, bool): return {"booleanValue": v}
    if isinstance(v, int): return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, str): return {"stringValue": v}
    if isinstance(v, list): return {"arrayValue": {"values": [enc(x) for x in v]}}
    if isinstance(v, dict): return {"mapValue": {"fields": {k: enc(x) for k, x in v.items()}}}
    raise TypeError(type(v))


def dec(v):
    (t, x), = v.items()
    if t == "nullValue": return None
    if t == "integerValue": return int(x)
    if t == "arrayValue": return [dec(i) for i in x.get("values", [])]
    if t == "mapValue": return {k: dec(i) for k, i in x.get("fields", {}).items()}
    return x  # string, boolean, double, timestamp, reference...


def doc_out(d):
    out = {"id": d["name"].rsplit("/", 1)[1]}
    out.update({k: dec(v) for k, v in d.get("fields", {}).items()})
    return out


# ---- operations -------------------------------------------------------------
def list_docs(path):
    docs, page = [], None
    while True:
        url = f"{BASE}/{path}?pageSize=300" + (f"&pageToken={page}" if page else "")
        res = _req("GET", url)
        docs += [doc_out(d) for d in res.get("documents", [])]
        page = res.get("nextPageToken")
        if not page:
            return docs


def get(c, i): return doc_out(_req("GET", f"{BASE}/{COLL[c]}/{i}"))


def put(c, i, data):
    return doc_out(_req("PATCH", f"{BASE}/{COLL[c]}/{i}", {"fields": {k: enc(v) for k, v in data.items() if k != "id"}}))


def update(c, i, data):
    data = {k: v for k, v in data.items() if k != "id"}
    mask = "&".join("updateMask.fieldPaths=" + urllib.request.quote(f"`{k}`" if not k.isidentifier() else k) for k in data)
    return doc_out(_req("PATCH", f"{BASE}/{COLL[c]}/{i}?{mask}", {"fields": {k: enc(v) for k, v in data.items()}}))


def delete(c, i): _req("DELETE", f"{BASE}/{COLL[c]}/{i}"); return {"deleted": i}


def add(c, data): return doc_out(_req("POST", f"{BASE}/{COLL[c]}", {"fields": {k: enc(v) for k, v in data.items()}}))


def _json(arg): return json.load(sys.stdin) if arg == "-" else json.loads(arg)


def main(a):
    if not a: sys.exit(__doc__)
    op = a[0]
    if op == "list": r = list_docs(COLL[a[1]])
    elif op == "get": r = get(a[1], a[2])
    elif op == "set": r = put(a[1], a[2], _json(a[3]))
    elif op == "update": r = update(a[1], a[2], _json(a[3]))
    elif op == "delete": r = delete(a[1], a[2])
    elif op == "add": r = add(a[1], _json(a[2]))
    elif op == "comments": r = list_docs(f"hs_units/{a[1]}/comments")
    elif op == "import":
        rows = json.load(open(a[2]))
        r = [put(a[1], x["id"], x)["id"] for x in rows]
    else: sys.exit(__doc__)
    print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
