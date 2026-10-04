"""KrishiKavach local server — standard library only, no installs needed.

Run:  python server.py        then open http://127.0.0.1:8000
"""

import json
import os
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import chatbot
import recommender as R

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, "static")
DATA = os.path.join(ROOT, "data")
FEEDBACK_FILE = os.path.join(DATA, "feedback.json")
PORT = int(os.environ.get("PORT", "8000"))
# 127.0.0.1 = this computer only. Set HOST=0.0.0.0 to serve other devices / cloud (Codespaces, Render).
HOST = os.environ.get("HOST", "127.0.0.1")

_lock = threading.Lock()


def load_feedback():
    try:
        with open(FEEDBACK_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_feedback(items):
    os.makedirs(DATA, exist_ok=True)
    tmp = FEEDBACK_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    os.replace(tmp, FEEDBACK_FILE)


def local_images():
    """Photo keys saved in static/img/<key>.jpg (used before the online copy)."""
    folder = os.path.join(STATIC, "img")
    if not os.path.isdir(folder):
        return []
    return sorted(f[:-4] for f in os.listdir(folder) if f.endswith(".jpg"))


def feedback_summary(district=None):
    items = load_feedback()
    by_crop = {}
    for it in items:
        if district and it.get("district") != district:
            continue
        s = by_crop.setdefault(it["crop"], {"count": 0, "good": 0, "quintals": 0.0})
        s["count"] += 1
        s["good"] += 1 if it.get("rating") == "good" else 0
        s["quintals"] += float(it.get("quintals") or 0)
    for s in by_crop.values():
        s["avg_quintals"] = round(s["quintals"] / s["count"], 1) if s["count"] else 0
        del s["quintals"]
    total = sum(1 for it in items if not district or it.get("district") == district)
    return {"total": total, "all_total": len(items), "by_crop": by_crop}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=STATIC, **kw)

    def log_message(self, fmt, *args):
        print("[%s] %s" % (time.strftime("%H:%M:%S"), fmt % args))

    # ---- helpers
    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 100_000:
            raise ValueError("too large")
        return json.loads(self.rfile.read(n) or b"{}")

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    # ---- routes
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/meta":
            return self._json({
                "outlook": R.OUTLOOK,
                "districts": {k: {l: v[l] for l in ("en", "mr", "hi")} | {"normal_rain": v["normal_rain"]}
                              for k, v in R.DISTRICTS.items()},
                "crops": {k: {"name": c["name"], "season": c["season"], "tips": c["tips"],
                              "sow": c["sow"], "harvest": c["harvest"], "days": c["days"]}
                          for k, c in R.CROPS.items()},
                "chat_mode": chatbot.mode(),
                "local_images": local_images(),
            })
        if url.path == "/api/feedback/summary":
            q = dict(p.split("=", 1) for p in url.query.split("&") if "=" in p)
            return self._json(feedback_summary(q.get("district")))
        if url.path.startswith("/api/"):
            return self._json({"error": "not found"}, 404)
        return super().do_GET()

    def do_POST(self):
        url = urlparse(self.path)
        try:
            data = self._body()
        except (ValueError, json.JSONDecodeError):
            return self._json({"error": "bad json"}, 400)

        if url.path == "/api/recommend":
            try:
                res = R.recommend(data.get("district"), data.get("soil"), data.get("water"), data.get("season"))
            except ValueError as e:
                return self._json({"error": str(e)}, 400)
            summary = feedback_summary(data.get("district"))["by_crop"]
            for c in res["crops"]:
                c["community"] = summary.get(c["id"])
            return self._json(res)

        if url.path == "/api/chat":
            res = chatbot.reply(data.get("message", ""), data.get("lang", "mr"),
                                data.get("profile"), data.get("history"))
            return self._json(res)

        if url.path == "/api/feedback":
            crop = data.get("crop")
            if crop not in R.CROPS or data.get("rating") not in ("good", "okay", "bad"):
                return self._json({"error": "bad input"}, 400)
            item = {
                "crop": crop,
                "district": data.get("district") if data.get("district") in R.DISTRICTS else None,
                "quintals": max(0.0, min(100.0, float(data.get("quintals") or 0))),
                "rating": data["rating"],
                "season": data.get("season"),
                "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            with _lock:
                items = load_feedback()
                items.append(item)
                save_feedback(items)
            return self._json({"ok": True, "summary": feedback_summary(item["district"])})

        return self._json({"error": "not found"}, 404)


if __name__ == "__main__":
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"KrishiKavach running at http://{HOST}:{PORT}  (chatbot mode: {chatbot.mode()})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
