from flask import Flask, render_template, request, jsonify, abort
import uuid
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

store = {}
STORE_FILE = os.path.join(BASE_DIR, "data.json")

def load_store():
    global store
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "r") as f:
            store = json.load(f)

def save_store():
    with open(STORE_FILE, "w") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

load_store()

def get_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/create", methods=["POST"])
def create():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Metin boş olamaz"}), 400
    if len(text) > 1000:
        return jsonify({"error": "Metin çok uzun (max 1000 karakter)"}), 400

    entry_id = str(uuid.uuid4())[:8]
    owner_token = str(uuid.uuid4())  # Gizli sahip tokeni

    store[entry_id] = {
        "text": text,
        "created_at": datetime.now().isoformat(),
        "owner_token": owner_token,
        "view_count": 0,
        "views": [],
        "replies": [],
        "replied_ips": []
    }
    save_store()

    view_url = request.host_url + "view/" + entry_id
    # Owner URL'e token ekliyoruz
    owner_url = request.host_url + "view/" + entry_id + "?token=" + owner_token
    return jsonify({"id": entry_id, "url": view_url, "owner_url": owner_url, "owner_token": owner_token})


@app.route("/api/list")
def list_qr():
    items = []
    for eid, entry in store.items():
        items.append({
            "id": eid,
            "text_preview": entry["text"][:60] + ("…" if len(entry["text"]) > 60 else ""),
            "created_at": entry["created_at"],
            "view_count": entry.get("view_count", 0),
            "reply_count": len(entry.get("replies", []))
        })
    # En yeni en üstte
    items.sort(key=lambda x: x["created_at"], reverse=True)
    return jsonify(items)

@app.route("/view/<entry_id>")
def view(entry_id):
    entry = store.get(entry_id)
    if not entry:
        abort(404)

    ip = get_ip()
    token = request.args.get("token", "")
    is_owner = (token == entry.get("owner_token", ""))

    entry.setdefault("view_count", 0)
    entry.setdefault("views", [])
    entry.setdefault("replies", [])
    entry.setdefault("replied_ips", [])

    # Sahip görüntülemesi sayılmasın
    if not is_owner:
        entry["view_count"] += 1
        entry["views"].append(datetime.now().isoformat())
        entry["views"] = entry["views"][-50:]
        save_store()

    already_replied = ip in entry["replied_ips"]

    return render_template(
        "view.html",
        text=entry["text"],
        created_at=entry["created_at"],
        entry_id=entry_id,
        view_count=entry["view_count"],
        last_views=entry["views"][-5:][::-1],
        replies=entry["replies"],
        already_replied=already_replied,
        is_owner=is_owner,
        owner_token=entry.get("owner_token", "") if is_owner else ""
    )

# Ziyaretçi mesaj bırakır
@app.route("/api/reply/<entry_id>", methods=["POST"])
def reply(entry_id):
    entry = store.get(entry_id)
    if not entry:
        return jsonify({"error": "Bulunamadı"}), 404

    ip = get_ip()
    if ip in entry.get("replied_ips", []):
        return jsonify({"error": "Zaten bir mesaj bıraktın!"}), 403

    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Mesaj boş olamaz"}), 400
    if len(text) > 500:
        return jsonify({"error": "Mesaj çok uzun (max 500 karakter)"}), 400

    reply_id = str(uuid.uuid4())[:8]
    entry.setdefault("replied_ips", []).append(ip)
    entry.setdefault("replies", []).append({
        "id": reply_id,
        "text": text,
        "created_at": datetime.now().isoformat(),
        "owner_reply": None
    })
    save_store()
    return jsonify({"ok": True, "reply_id": reply_id})

# Sahip token ile cevap verir
@app.route("/api/owner-reply/<entry_id>/<reply_id>", methods=["POST"])
def owner_reply(entry_id, reply_id):
    entry = store.get(entry_id)
    if not entry:
        return jsonify({"error": "Bulunamadı"}), 404

    data = request.get_json()
    token = data.get("token", "")
    if not token or token != entry.get("owner_token", ""):
        return jsonify({"error": "Yetkisiz erişim!"}), 403

    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Cevap boş olamaz"}), 400
    if len(text) > 500:
        return jsonify({"error": "Cevap çok uzun (max 500 karakter)"}), 400

    for r in entry.get("replies", []):
        if r["id"] == reply_id:
            r["owner_reply"] = {
                "text": text,
                "created_at": datetime.now().isoformat()
            }
            save_store()
            return jsonify({"ok": True})

    return jsonify({"error": "Mesaj bulunamadı"}), 404

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        pass
    print(f"\n🚀 QR App çalışıyor!")
    print(f"   Local:   http://127.0.0.1:5000")
    print(f"   Network: http://{local_ip}:5000")
    print(f"\n   ⚠️  Aynı WiFi'deki cihazlardan erişmek için Network adresini kullanın\n")
    app.run(debug=True, host="0.0.0.0", port=5000)