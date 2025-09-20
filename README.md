# AI Automation Telegram Bot (n8n JSON Generator)

بوت تيليغرام يولّد ملفات **n8n JSON** قابلة للاستيراد، بالاعتماد على **OpenRouter API** + دعم مكتبة قوالب جاهزة اختيارية.

## النشر على Render (خدمة ويب واحدة)
1. أنشئ مستودع GitHub وارفع هذا المشروع.
2. في Render: **New → Web Service** (اختَر Python) واربط بالمستودع.
3. اترك `buildCommand` و `startCommand` كما في `render.yaml` أو فعّل Auto-Deploy.
4. أضِف Environment Variables:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENROUTER_API_KEY` (اختياري؛ إن لم تضفها ستحصل على أمثلة جاهزة فقط)
   - `OPENROUTER_MODEL` (اختياري، افتراضي: `openai/gpt-4o-mini`)
   - `WEBHOOK_SECRET` (string؛ أو اجعله auto/generate كما في render.yaml)

> **مهم:** هذا المشروع يعمل كـ **Web Service واحد فقط**.

## إعداد Webhook لتيليغرام
افترض أن دومين Render هو: `https://your-app.onrender.com`  
المسار السري: `/webhook/<WEBHOOK_SECRET>`

نفّذ (مرّة واحدة):
```
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://your-app.onrender.com/webhook/<WEBHOOK_SECRET>
```

للإلغاء:
```
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/deleteWebhook
```

## استخدام مكتبة القوالب
ضع ملفك `data/workflows_library.json` بنفس البنية:
```json
[
  {
    "name": "Title",
    "tags": ["tag1", "tag2"],
    "summary": "What this does",
    "json": { "...": "n8n file content" }
  }
]
```
البوت سيبحث بكلمات مفتاحية داخل `name/tags/summary` ويستأنس بها أثناء التوليد.

## ملاحظات حول n8n JSON
- سيحافظ على المفاتيح الأساسية: `name, nodes, connections, settings, tags`.
- يضمن IDs فريدة وروابط صحيحة بين العقد (أو يصل أوّل عقدتين كحد أدنى).
- يُفضّل المراجع البيئية داخل n8n مثل: `={{$env.VAR}}` بدل الأسرار الصريحة.
