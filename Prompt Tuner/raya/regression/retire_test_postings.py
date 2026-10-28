#!/usr/bin/env python3
"""retire_test_postings.py: retire every job posting that a test call left on one of OUR test numbers.

The nightly sweep and /voice-test post real jobs from the DKB bots (that is what they test). Left live,
those posts are read to real job seekers ("Tuner Staffing Unit 4" stayed live for four days in
October 2026). Run this after every sweep. It only ever touches participants whose phone is in our
own 91888888xxxx test block, and only their job_posting_1.0 items.

  python3 raya/regression/retire_test_postings.py            # retire
  python3 raya/regression/retire_test_postings.py --dry-run  # list only
"""
import glob, json, os, re, sys, urllib.error, urllib.parse, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "raya/overnight"))
from overnight_sweep import raya_get  # noqa: E402

TEST_BLOCK = re.compile(r"^(91)?8888888\d{3}$")
# one DKB Signals agent per job-board instance; its create_job tool carries that instance's url + auth
INSTANCE_AGENTS = ("dkb-hi-signals", "dkb-kn-signals")


def agent_uuid(target):
    for t in json.load(open(os.path.join(REPO, "raya/agents.json")))["targets"]:
        if t["id"] == target:
            return (t.get("raya_agent_id") or {}).get("prod")


def instance_api(target):
    a = raya_get("/api/agent/" + agent_uuid(target))
    tool = next(t for t in a["tools"]["llm_tools"] if t["function"]["name"] == "create_job")["api_details"]
    headers = dict(tool.get("header") or {})
    headers["Content-Type"] = "application/json"
    return tool["url"].split("/api/")[0], headers


def call(base, headers, method, path, body=None, query=None):
    url = base + path + ("?" + urllib.parse.urlencode(query) if query else "")
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers, method=method), timeout=60) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]


def test_numbers():
    nums = set()
    for f in glob.glob(os.path.join(REPO, "raya/testcases/args/**/*.json"), recursive=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        for k in ("phoneNumber", "contact_phone"):
            v = re.sub(r"\D", "", str(d.get(k, "")))
            if TEST_BLOCK.match(v):
                nums.add(v[-10:])
    return sorted(nums)


def main():
    dry = "--dry-run" in sys.argv
    nums = test_numbers()
    retired = 0
    for target in INSTANCE_AGENTS:
        base, headers = instance_api(target)
        for n in nums:
            s, r = call(base, headers, "GET", "/api/v1/admin/participant", query={"phone_number": "+91" + n})
            if s != 200 or not isinstance(r, dict):
                continue
            for it in r.get("items") or []:
                if it.get("item_type") != "job_posting_1.0" or it.get("lifecycle_status") == "retired":
                    continue
                name = (it.get("item_state") or {}).get("jobProviderName") or ""
                print(f"{target[4:6]} XXXXXX{n[-4:]} {it['item_id']} {it['lifecycle_status']} {name}")
                if not dry:
                    s2, r2 = call(base, headers, "POST", "/api/v1/item/lifecycle",
                                  {"item_id": it["item_id"], "action": "retire"})
                    print("   retire ->", s2)
                    retired += s2 == 200
    print(f"{len(nums)} test numbers checked, {retired} postings retired{' (dry run)' if dry else ''}")


if __name__ == "__main__":
    main()
