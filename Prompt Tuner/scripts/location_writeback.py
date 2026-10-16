#!/usr/bin/env python3
"""location_writeback.py — after a call, write the caller's location to their Signals profile so the
backend re-geocodes it into item_locations (the map point "jobs near you" matching runs on).

Why post-call, not in-call. Three in-call designs were tried on 2026-09-23 (KKB Slim Hindi):
  * riding the job fetch       -> the bot skipped the location questions (~2/7 asked, vs 4/4 before)
  * riding the services step   -> questions protected, but the save was lost when the call ended
                                  early, and forgotten when it did not (1/2 even when reached)
Meanwhile the OUTPUT prompt captured the landmark and pin on 5/5 calls, including the ones where the
in-call save failed. So the data is already there after every call; this script only writes it.
Nothing runs during the call, so nothing can affect it.

The backend geocodes the `location` string itself on every write (verified 9/9 updates re-geocode;
0.15-0.76 km from OpenStreetMap where a reference exists). No external geocoder is needed.

SAFETY (the reason this is code and not a tool the model calls):
  * The phone is the number the BOT used for get_profile in that call, normalised here — never
    model-constructed. A doubled 91 prefix minted a phantom user on call 482ea2e2.
  * It never writes unless get_profile resolves that phone to an EXISTING user who owns a live seeker
    profile. The endpoint finds-or-creates by phone, so this check is what makes a phantom impossible.
  * Only item_state.location is sent. Idempotent: skips when the stored value is already current.

Usage:
  python3 scripts/location_writeback.py plan  [--agent UUID] [--limit N] [--calls U1,U2]
  python3 scripts/location_writeback.py apply [--agent UUID] [--limit N] [--calls U1,U2]
Default agent: kkb-hi-signals-slim. `plan` writes nothing.
"""
import argparse, json, math, os, re, sys, urllib.error, urllib.parse, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env = {}
for _l in open(os.path.join(REPO, "raya/.env")):
    _l = _l.strip()
    if "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        _env[k.strip()] = v.strip().strip('"').strip("'")
RAYA, TOKEN = _env["RAYA_BASE_URL"].rstrip("/"), _env["RAYA_API_TOKEN"]
SLIM = "140d13ca-c80f-47c4-9454-5edb3fd38c96"
STATE = os.path.join(REPO, "raya/location-writeback-state.json")
NA = {"", "na", "n/a", "none", "null", "unknown", "not available"}


def raya(path):
    r = urllib.request.Request(RAYA + path, headers={"X-API-Key": TOKEN, "User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(r, timeout=90))
    return d.get("data", d) if isinstance(d.get("data"), dict) else d


def tools_of(agent):
    a = raya("/api/agent/" + agent)
    return {(t.get("function") or {}).get("name"): t for t in (a.get("tools") or {}).get("llm_tools") or []}


def normalise_phone(raw):
    """12 digits starting 91. Returns None for anything it cannot make sense of — never guesses."""
    d = re.sub(r"\D", "", str(raw or ""))
    if len(d) == 12 and d.startswith("91"):
        return d
    if len(d) == 10:
        return "91" + d
    return None


def usable(v):
    return v is not None and str(v).strip().lower() not in NA


def title(s):
    return " ".join(w if w.isupper() and len(w) > 1 else w[:1].upper() + w[1:] for w in str(s).split())


def km(p, q):
    R = 6371
    a1, o1, a2, o2 = map(math.radians, [p[0], p[1], q[0], q[1]])
    h = math.sin((a2 - a1) / 2) ** 2 + math.cos(a1) * math.cos(a2) * math.sin((o2 - o1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def city_state(stored):
    """The last two place names before 'India' in the stored location — the city and the state."""
    parts = [p.strip() for p in str(stored or "").split(",") if p.strip()]
    while parts and parts[-1].lower() in ("india", "भारत"):
        parts = parts[:-1]
    parts = [re.sub(r"\s*\b\d{6}\b", "", p).strip() for p in parts]   # a stored PIN is re-added once
    parts = [p for p in parts if p]
    return parts[-2:] if len(parts) >= 2 else parts


def compose(landmark, area, stored, pin=None):
    """One address string, because the DPG profile has ONE location field (agreed 2026-10-13):
    '<landmark>, <area>, <City>, <State> <PIN>, India'. The PIN goes in only when it is exactly six digits."""
    out, seen = [], set()
    pieces = []
    for v in [title(landmark) if usable(landmark) else "", title(area) if usable(area) else ""]:
        pieces += [x.strip() for x in v.split(",")]           # "Loni, Ghaziabad" is two places
    for p in [*pieces, *city_state(stored), "India"]:
        if p and p.lower().replace(" ", "") not in seen:
            out.append(p)
            seen.add(p.lower().replace(" ", ""))
    pin = re.sub(r"\D", "", str(pin or ""))
    if len(pin) == 6 and len(out) >= 2 and pin not in ", ".join(out):
        out[-2] = f"{out[-2]} {pin}"
    return ", ".join(out)


def phone_bot_used(transcript):
    for t in transcript:
        for f in t.get("tool_calls") or []:
            if f["function"]["name"] == "get_profile":
                try:
                    return json.loads(f["function"]["arguments"]).get("phone_number")
                except Exception:
                    return None
    return None


def area_fallback(call):
    """For calls made before home_area existed: the pre-call ${location}, minus any PIN."""
    loc = (call.get("agent_args") or {}).get("location") or ""
    return re.sub(r"\b\d{6}\b", "", loc).strip(" ,") or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["plan", "apply"])
    ap.add_argument("--agent", default=SLIM)
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--calls", default="")
    a = ap.parse_args()

    T = tools_of(a.agent)
    gp, up = T["get_profile"], T["update_profile"]           # endpoint + auth cloned from the live agent
    GH = dict(gp["api_details"].get("header") or {})
    UH = dict(up["api_details"].get("header") or {}); UH["Content-Type"] = "application/json"
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"processed": {}}

    if a.calls:
        uuids = [u.strip() for u in a.calls.split(",") if u.strip()]
    else:
        lst = raya(f"/api/call?agent_id={a.agent}&limit={a.limit}")
        uuids = [c["uuid"] for c in lst.get("calls") or [] if c.get("outcome") == "Completed"]

    # OLDEST FIRST, so when one caller has several calls the latest location is the one that stays.
    # (The list API is newest-first; processing it as-is let an older call overwrite a newer address.)
    todo = []
    for u in uuids:
        if u in state["processed"] and a.mode == "apply":
            print(f"{u[:8]}  skip — already processed"); continue
        todo.append((u, raya("/api/call/" + u)))
    todo.sort(key=lambda x: x[1].get("created_at") or "")
    for u, c in todo:
        tag = u[:8]
        out = c.get("call_output") or {}
        # READINESS: the output prompt runs AFTER the call and lags. Reading it too early gives nulls,
        # and falling back to the pre-call ${location} then writes where the caller USED to live
        # (call 6c12ef52 wrote Muradnagar for a caller who had just moved to Modinagar). Not ready ->
        # skip WITHOUT recording, so the next run picks it up.
        if "nearest_landmark" not in out:
            print(f"{tag}  skip — call record not ready yet (retry later)"); continue
        landmark, area = out.get("nearest_landmark"), out.get("home_area")
        precall = area_fallback(c)
        if "home_area" not in out and not usable(area):
            area = precall                     # legacy calls only: made before home_area existed
        # STALE LANDMARK after a move: it names the OLD area but not the caller's final one.
        if (usable(landmark) and usable(area) and precall and area.lower() != precall.lower()
                and area.lower() not in landmark.lower() and precall.lower() in landmark.lower()):
            print(f"{tag}  note — dropping landmark {landmark!r}: it names {precall!r}, but the caller now lives in {area!r}")
            landmark = None
        if not usable(landmark) and not usable(area):
            print(f"{tag}  skip — no location captured on this call"); continue
        phone = normalise_phone(phone_bot_used(c.get("call_transcript") or []))
        if not phone:
            print(f"{tag}  skip — could not determine the caller's phone safely"); continue

        q = gp["api_details"]["url"] + "?" + urllib.parse.urlencode({"phone_number": phone})
        try:
            prof = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=GH), timeout=40))
        except urllib.error.HTTPError as e:      # e.g. 400 U18_NOT_ALLOWED: no writable profile
            print(f"{tag}  skip — profile lookup refused ({e.code})"); continue
        if not prof.get("user_id"):
            print(f"{tag}  skip — {phone} is not an existing user (writing would CREATE one)"); continue
        live = [i for i in prof.get("items") or []
                if i.get("item_domain") == "seeker" and i.get("lifecycle_status") == "live"]
        if not live:
            print(f"{tag}  skip — no live seeker profile for {phone}"); continue
        it = live[0]; st = it.get("item_state") or {}
        stored = st.get("location") or ""
        new = compose(landmark, area, stored, out.get("pin_code"))
        if new.lower() == stored.lower():
            print(f"{tag}  skip — already current: {stored}"); continue
        before = (it.get("item_locations") or [{}])[0]
        print(f"{tag}  {stored!r}\n        -> {new!r}")
        if a.mode == "plan":
            continue

        body = {"age": st.get("age"), "name": st.get("name"), "phone_number": "+" + phone,
                "domain": "seeker", "channel": "voice", "network": "blue_dot", "item_type": "profile_1.0",
                "item_id": it["item_id"], "item_state": {"location": new}}
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(
                up["api_details"]["url"], data=json.dumps(body).encode(), headers=UH, method="POST"), timeout=60))
        except urllib.error.HTTPError as e:
            print(f"        WRITE FAILED {e.code}: {e.read().decode()[:200]}"); continue
        if r.get("user_existed") is not True:
            print("        !! backend reports a NEW user — stopping; investigate before continuing"); sys.exit(2)
        after = raya_point(gp, GH, phone)
        moved = km((before.get("lat"), before.get("lng")), after) if before.get("lat") else None
        print(f"        written. point {after[0]:.5f},{after[1]:.5f}"
              + (f"  (moved {moved:.2f} km)" if moved is not None else ""))
        state["processed"][u] = {"location": new, "point": after}
        json.dump(state, open(STATE, "w"), indent=1)


def raya_point(gp, GH, phone):
    q = gp["api_details"]["url"] + "?" + urllib.parse.urlencode({"phone_number": phone})
    prof = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=GH), timeout=40))
    it = [i for i in prof.get("items") or [] if i.get("item_domain") == "seeker" and i.get("lifecycle_status") == "live"][0]
    p = (it.get("item_locations") or [{}])[0]
    return (p.get("lat"), p.get("lng"))


if __name__ == "__main__":
    main()
