# دليل النشر على Render.com

## نظرة عامة
هذا المشروع مُعد للنشر على منصة Render.com باستخدام Blueprint Deploy. يحتوي ملف `render.yaml` على تكوين شامل لجميع الخدمات المطلوبة.

## الخدمات المشمولة

### 1. Backend API (FastAPI)
- **الاسم**: `ai-callcenter-backend`
- **البيئة**: Python
- **الوصف**: API خلفي لمعالجة المكالمات الصوتية وتحليلها
- **الصحة**: `/health`

### 2. Frontend (Next.js)
- **الاسم**: `ai-callcenter-frontend`
- **البيئة**: Node.js
- **الوصف**: واجهة مستخدم للوحة التحكم

### 3. Worker (Celery)
- **الاسم**: `ai-callcenter-worker`
- **البيئة**: Python
- **الوصف**: معالج المهام الخلفية للصوتيات والتحليل

### 4. Beat Scheduler (اختياري)
- **الاسم**: `ai-callcenter-beat`
- **البيئة**: Python
- **الوصف**: جدولة المهام الدورية

## قواعد البيانات المدارة

### PostgreSQL
- **الاسم**: `callcenter-db`
- **المخطط**: `callcenter_db`
- **المستخدم**: `callcenter_user`

### Redis
- **الاسم**: `callcenter-redis`
- **الغرض**: تخزين مؤقت ووسيط رسائل Celery

## خطوات النشر

### 1. التحضير
```bash
# تأكد من وجود جميع الملفات المطلوبة
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. إنشاء حساب Render
1. اذهب إلى [render.com](https://render.com)
2. أنشئ حساب جديد أو سجل دخول
3. اربط حساب GitHub الخاص بك

### 3. النشر باستخدام Blueprint
1. في لوحة تحكم Render، اختر **"New +"**
2. اختر **"Blueprint"**
3. اربط مستودع GitHub الخاص بك
4. اختر المستودع `mvpvoice`
5. سيقرأ Render ملف `render.yaml` تلقائياً

### 4. إعداد متغيرات البيئة المطلوبة

#### متغيرات يجب إدخالها يدوياً:
```
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

#### متغيرات تُولد تلقائياً:
- `SECRET_KEY` (مولد تلقائياً)
- `DATABASE_URL` (من قاعدة البيانات المدارة)
- `REDIS_URL` (من Redis المدار)

### 5. ترتيب النشر
سيتم إنشاء الخدمات بالترتيب التالي:
1. قاعدة بيانات PostgreSQL
2. خدمة Redis
3. Backend API
4. Frontend
5. Celery Worker
6. Celery Beat (اختياري)

## التحقق من النشر

### 1. فحص الخدمات
```bash
# تحقق من صحة Backend
curl https://ai-callcenter-backend.onrender.com/health

# تحقق من Frontend
curl https://ai-callcenter-frontend.onrender.com
```

### 2. فحص قواعد البيانات
- تأكد من اتصال PostgreSQL
- تأكد من عمل Redis
- تحقق من تشغيل مهام Celery

### 3. السجلات
راجع سجلات كل خدمة في لوحة تحكم Render للتأكد من عدم وجود أخطاء.

## التحديثات

### النشر التلقائي
النشر التلقائي مُعطل (`autoDeploy: false`) لتجنب النشر غير المرغوب فيه.

### النشر اليدوي
1. ادفع التغييرات إلى المستودع
2. اذهب إلى لوحة تحكم Render
3. اختر الخدمة المطلوب تحديثها
4. اضغط **"Manual Deploy"**

## استكشاف الأخطاء

### مشاكل شائعة:

#### 1. فشل تثبيت Dependencies
```bash
# في Backend
cd backend && pip install --upgrade pip && pip install -r requirements.txt

# في Frontend
cd frontend && npm ci
```

#### 2. مشاكل قاعدة البيانات
- تأكد من صحة `DATABASE_URL`
- تحقق من تشغيل migrations: `alembic upgrade head`

#### 3. مشاكل Celery
- تأكد من صحة `REDIS_URL`
- تحقق من تشغيل Redis
- راجع إعدادات `CELERY_BROKER_URL`

#### 4. مشاكل Next.js
- تأكد من صحة `NEXT_PUBLIC_API_URL`
- تحقق من build process: `npm run build`

## الأمان

### متغيرات البيئة الحساسة
- لا تضع مفاتيح API في الكود
- استخدم `sync: false` للمتغيرات الحساسة
- فعّل `generateValue: true` للمفاتيح السرية

### CORS
تأكد من تحديث إعدادات CORS في الإنتاج:
```python
# في main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## الدعم
للحصول على المساعدة:
1. راجع [وثائق Render](https://render.com/docs)
2. تحقق من سجلات الخدمات
3. راجع [مجتمع Render](https://community.render.com)

---
تم إعداد هذا الدليل لمساعدتك في نشر المشروع بنجاح على منصة Render.com
