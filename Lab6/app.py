import json
import os
import urllib.error
import urllib.request
import uuid
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


# =========================
# Environment Variables
# =========================

load_dotenv()

# OpenRouter（OpenAI 相容 Chat Completions API）
# API Key 申請：https://openrouter.ai/keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
).rstrip("/")
# 模型清單：https://openrouter.ai/models
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4o-mini",
)
SECRET_KEY = os.getenv("SECRET_KEY")

if (
    not OPENROUTER_API_KEY
    or OPENROUTER_API_KEY == "YOUR_API_KEY_HERE"
):
    raise RuntimeError(
        "找不到 OPENROUTER_API_KEY，請先建立 .env 並填入 API Key。"
    )

if not SECRET_KEY or SECRET_KEY == "CHANGE_ME":
    raise RuntimeError(
        "請在 .env 設定安全的 SECRET_KEY。"
    )


# =========================
# Flask
# =========================

app = Flask(__name__)
app.secret_key = SECRET_KEY


# Lab 用簡化帳號
# 正式系統不應以明文保存密碼
USERS = {
    "admin": "1234",
}


# =========================
# OpenRouter
# =========================

# Flask 預設 Session 存在 Cookie（約 4KB 上限），
# 所以對話歷史存在伺服器記憶體，Session 只存對話 ID。
CONVERSATIONS = {}
MAX_HISTORY = 20


def ask_openrouter(
    message,
    conversation_id=None,
):
    if not conversation_id:
        conversation_id = uuid.uuid4().hex

    history = CONVERSATIONS.setdefault(
        conversation_id, []
    )
    history.append({
        "role": "user",
        "content": message,
    })

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + OPENROUTER_API_KEY,
        # 以下兩個為 OpenRouter 選填標頭（用於排行榜顯示）
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Lab6 Flask Chat",
    }

    req = urllib.request.Request(
        OPENROUTER_BASE_URL + "/chat/completions",
        data=json.dumps({
            "model": OPENROUTER_MODEL,
            "messages": history[-MAX_HISTORY:],
        }).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            req, timeout=60
        ) as resp:
            result = json.loads(
                resp.read().decode("utf-8")
            )
    except urllib.error.HTTPError as error:
        # 失敗時移除這次提問，避免歷史錯亂
        history.pop()
        detail = error.read().decode(
            "utf-8", errors="replace"
        )
        raise RuntimeError(
            f"HTTP {error.code}: {detail}"
        ) from error
    except Exception:
        history.pop()
        raise

    reply = (
        result["choices"][0]["message"]
        .get("content") or ""
    ).strip()

    if not reply:
        reply = "模型沒有回傳文字內容。"

    history.append({
        "role": "assistant",
        "content": reply,
    })
    del history[:-MAX_HISTORY]

    return reply, conversation_id


def ask_llm(message, previous_id=None):
    return ask_openrouter(message, previous_id)


BOT_NAME = OPENROUTER_MODEL


# =========================
# Login Required
# =========================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user" not in session:

            # API 不做 redirect
            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "請先登入"
                }), 401

            return redirect(
                url_for("login")
            )

        return view(*args, **kwargs)

    return wrapped


# =========================
# Login
# =========================

@app.route(
    "/",
    methods=["GET", "POST"],
)
def login():

    if request.method == "POST":

        username = (
            request.form
            .get("username", "")
            .strip()
        )

        password = request.form.get(
            "password",
            "",
        )

        if (
            username in USERS
            and USERS[username] == password
        ):

            session.clear()

            session["user"] = username

            return redirect(
                url_for("chat_room")
            )

        return render_template(
            "login.html",
            msg="帳號或密碼錯誤",
        )

    if "user" in session:
        return redirect(
            url_for("chat_room")
        )

    return render_template(
        "login.html"
    )


# =========================
# Chat Page
# =========================

@app.get("/chat")
@login_required
def chat_room():

    return render_template(
        "chat.html",
        username=session["user"],
    )


# =========================
# Chat API (OpenRouter)
# =========================

@app.post("/api/chat")
@login_required
def api_chat():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    message = str(
        data.get("message", "")
    ).strip()

    if not message:
        return jsonify({
            "error": "訊息不可為空"
        }), 400

    if len(message) > 2000:
        return jsonify({
            "error": "訊息過長"
        }), 400

    try:

        previous_id = session.get(
            "conversation_id"
        )

        reply, interaction_id = (
            ask_llm(
                message,
                previous_id,
            )
        )

        # 保存本次 interaction ID
        # 下一輪即可延續對話
        session[
            "conversation_id"
        ] = interaction_id

        return jsonify({
            "reply": reply,
            "bot": BOT_NAME,
        })

    except Exception as error:

        print(
            "[LLM API Error]",
            error,
        )

        return jsonify({
            "error":
            f"{BOT_NAME} API 呼叫失敗，"
            "請檢查 API Key、網路或模型設定。"
        }), 502


# =========================
# Reset Conversation
# =========================

@app.post("/api/reset")
@login_required
def reset_chat():

    old_id = session.pop(
        "conversation_id",
        None,
    )

    # 進階題：同時清除伺服器端的歷史
    CONVERSATIONS.pop(old_id, None)

    return jsonify({
        "ok": True
    })


# =========================
# Logout
# =========================

@app.post("/logout")
@login_required
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# Run Server
# =========================

if __name__ == "__main__":

    print(
        "=== Lab6 Flask Server ==="
    )

    print(
        "LLM Provider: "
        + "openrouter"
        + " / Model: "
        + OPENROUTER_MODEL
    )

    print(
        "Listening on "
        "http://0.0.0.0:3000"
    )

    print(
        "Debug mode is OFF"
    )

    app.run(
        host="0.0.0.0",
        port=3000,
        debug=False,
    )
