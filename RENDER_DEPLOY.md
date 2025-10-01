# نشر البوت على Render 🚀

## الخطوات:

### 1. تحميل الملفات إلى GitHub
```bash
git init
git add .
git commit -m "Discord Bot"
git remote add origin <your-github-repo>
git push -u origin main
```

### 2. إنشاء حساب على Render
- روح على https://render.com
- سجل دخول بحساب GitHub

### 3. إنشاء Background Worker
1. اضغط **"New +"** → اختر **"Background Worker"**
2. اربط حساب GitHub واختر المشروع
3. اعدادات البوت:
   - **Name**: اسم البوت (مثلاً: discord-bot)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

### 4. إضافة Environment Variables
في صفحة البوت، روح على **Environment** وأضف:
- `DISCORD_TOKEN` = توكن البوت من Discord
- `GOOGLE_API_KEY` = مفتاح Google Gemini API

### 5. Deploy
- اضغط **"Create Background Worker"**
- Render راح يبني وينشر البوت تلقائياً
- راقب الـ Logs عشان تشوف "البوت جاهز!"

## ملاحظات مهمة:

### الخطة المجانية
- ✅ 750 ساعة مجاناً كل شهر (حوالي 31 يوم)
- ⚠️ البوت قد يتوقف بعد فترة عدم نشاط طويلة
- 💡 للتشغيل 24/7 بدون توقف، استخدم الخطة المدفوعة ($7/شهر)

### مراقبة البوت
- استخدم صفحة **Logs** في Render لمراقبة نشاط البوت
- راح تشوف جميع الرسائل والأخطاء هناك

### التحديثات
- كل ما تسوي push على GitHub، Render راح يحدث البوت تلقائياً

## المساعدة
إذا واجهت مشاكل، شيك:
1. Environment Variables موجودة وصحيحة
2. الـ Logs ما فيها أخطاء
3. التوكن صحيح ونشط

البوت الحين جاهز للتشغيل 24/7! 🎉
