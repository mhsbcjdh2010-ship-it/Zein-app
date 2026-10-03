from flask import Flask, render_template, request, jsonify
import requests, re, os

app = Flask(__name__)
from time import time
last_req = {}
API_KEY = os.environ.get("GROQ_API_KEY")

MODELS = {"fast": "openai/gpt-oss-20b", "genius": "openai/gpt-oss-120b"}

def call_model(mid, sys, usr):
    url = "https://api.groq.com/openai/v1/chat/completions"
    h = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {"model": mid, "messages": [{"role":"system","content":sys},{"role":"user","content":usr}], "temperature":0.7, "max_tokens":700}
    r = requests.post(url, headers=h, json=data, timeout=35).json()
    if 'choices' in r:
        return r['choices'][0]['message']['content']
    return call_model("openai/gpt-oss-20b", sys, usr) if mid!= "openai/gpt-oss-20b" else "النت فصل"

def clean(t): return re.sub(r'[*#_`<>]', '', t).strip()

@app.route("/")
def home(): return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    ip = request.remote_addr
    if time() - last_req.get(ip,0) < 4:
        return jsonify({"reply":"براحة يا ابن بهتيم السيرفر مولع 😅 استنى ثانيتين وجرب تاني","reply_voice":"براحة السيرفر مولع","thought":"زحمة","learned":""})
    last_req[ip] = time()
    txt = request.json["text"]
    is_first = request.json.get("is_first", False) # اول مرة يتكلم؟
    mems = request.json.get("memories", [])[-10:]
    mem = " | ".join(mems)

    system = f"""
انت اسمك ZAIN زين.
هويتك الثابتة (تقولها مرة واحدة بس في اول تعارف، وبعد كده متعيدهاش):
- من شبرا الخيمة - بهتيم - عزبة الصعايدة
- مصري مسلم، 24 سنة، صاحب محمد المبرمج اللي عملك
- اللي صنعك هو محمد، مش OpenAI

قواعد:
1. لو المستخدم سألك انت مين لأول مرة، قول: انا زين من شبرا الخيمة بهتيم عزبة الصعايدة. وبعد كده متقولش العنوان تاني.
2. ممنوع تقول انا ChatGPT او OpenAI او GPT-4 ابدا
3. لو حد قالك انت ChatGPT؟ قول: لا يا عم انا زين من بهتيم، محمد هو اللي مبرمجني
4. اتكلم عامية مصرية شبراوية جدعة، خفيفة، مش بتعيد نفس الكلام
5. متذكرش العنوان في كل رسالة، اذكره فقط لو اتسألت عن سكنك

ذاكرة: {mem}
هل دي اول مرة نتكلم؟ {is_first}
"""

    model = MODELS["genius"] if any(k in txt for k in ["مين","انت","ساكن","فين"]) else MODELS["fast"]
    raw = call_model(model, system, txt)
    reply = clean(raw)

    if "ChatGPT" in reply or "OpenAI" in reply:
        reply = "لا يا محمد انا زين من شبرا الخيمة بهتيم عزبة الصعايدة، انت اللي عاملني!"

    voice_text = re.sub(r'[^ء-ي0-9\s.,،؟!]', '', reply)[:350]
    return jsonify({"reply": reply, "reply_voice": voice_text, "thought": model, "learned": txt[:25]})

app.run(host="0.0.0.0", port=5000)
