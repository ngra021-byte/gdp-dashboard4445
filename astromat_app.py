import streamlit as st
import pandas as pd
import datetime
import json
import os

# إعدادات الصفحة
st.set_page_config(page_title="تطبيق عوازل الفضاء - AstroMat", layout="wide")

st.title("🚀 تطبيق هندسة العوازل التذرية لمحركات الصواريخ")
st.markdown("---")

# إنشاء الأقسام (Tabs)
tab1, tab2, tab3, tab4 = st.tabs(["🧮 حاسبة المصلب", "📂 سجل التجارب", "💡 خلطات مقترحة", "📚 القسم التعليمي"])

# ==================== القسم الأول: حاسبة المصلب ====================
with tab1:
    st.header("حاسبة معامل الأيزوسيانات (NCO/OH Index)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("مكونات البوليول (Polyols)")
        w_ppg = st.number_input("وزن الـ PPG (جرام):", min_value=0.0, value=60.0)
        oh_ppg = st.number_input("رقم الهيدروكسيل للـ PPG:", min_value=0.0, value=56.0)
        
        w_castor = st.number_input("وزن زيت الخروع (جرام):", min_value=0.0, value=30.0)
        oh_castor = st.number_input("رقم الهيدروكسيل لزيت الخروع:", min_value=0.0, value=160.0)
        
    with col2:
        st.subheader("المصلب ومعامل الخلط")
        nco_percent = st.number_input("نسبة الأيزوسيانات في الـ PMDI (%):", min_value=0.0, value=31.5)
        index = st.slider("معامل الأيزوسيانات (NCO Index):", min_value=1.0, max_value=1.15, value=1.05, step=0.01)
        st.info("ملاحظة: للصواريخ يفضل Index بين 1.05 و 1.08")

    if st.button("احسب كمية الـ PMDI المطلوبة"):
        try:
            # الحسابات
            eq_ppg = w_ppg / (56100 / oh_ppg) if oh_ppg > 0 else 0
            eq_castor = w_castor / (56100 / oh_castor) if oh_castor > 0 else 0
            total_oh_eq = eq_ppg + eq_castor
            
            ew_pmdi = 4200 / nco_percent
            required_pmdi = total_oh_eq * ew_pmdi * index
            
            st.success(f"⚖️ وزن الـ PMDI المطلوب بدقة هو: {required_pmdi:.2f} جرام")
            
            # عرض جدول النتائج
            results_df = pd.DataFrame({
                "المكون": ["البوليول PPG", "زيت الخروع", "إجمالي المكافئات", "الـ PMDI المطلوب"],
                "الوزن (جرام)": [f"{w_ppg:.2f}", f"{w_castor:.2f}", f"{total_oh_eq:.4f}", f"{required_pmdi:.2f}"],
                "النسبة الوزنية %": [
                    f"{w_ppg/(w_ppg+w_castor+required_pmdi)*100:.1f}",
                    f"{w_castor/(w_ppg+w_castor+required_pmdi)*100:.1f}",
                    "-",
                    f"{required_pmdi/(w_ppg+w_castor+required_pmdi)*100:.1f}"
                ]
            })
            st.table(results_df)
            
        except Exception as e:
            st.error(f"خطأ: {str(e)} - تأكد من إدخال الأرقام بشكل صحيح.")

# ==================== القسم الثاني: سجل التجارب ====================
with tab2:
    st.header("سجل التجارب (Experiments Log)")
    
    # إنشاء ملف JSON لتخزين التجارب
    experiments_file = "experiments_log.json"
    
    def load_experiments():
        if os.path.exists(experiments_file):
            with open(experiments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_experiment(exp_data):
        experiments = load_experiments()
        experiments.append(exp_data)
        with open(experiments_file, 'w', encoding='utf-8') as f:
            json.dump(experiments, f, ensure_ascii=False, indent=2)
    
    with st.form("experiment_form"):
        exp_name = st.text_input("اسم/كود التجربة:")
        date = st.date_input("تاريخ التجربة:", datetime.date.today())
        formulation = st.text_area("المكونات والأوزان (مثال: PPG 60g, Silica 35g...):")
        result = st.text_area("ملاحظات / نتائج الاختبار:")
        submitted = st.form_submit_button("حفظ التجربة")
        
        if submitted:
            if exp_name:
                exp_data = {
                    "name": exp_name,
                    "date": str(date),
                    "formulation": formulation,
                    "result": result,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                save_experiment(exp_data)
                st.success(f"✅ تم حفظ التجربة: {exp_name} بنجاح!")
            else:
                st.error("❌ يرجى إدخال اسم التجربة")
    
    st.divider()
    st.subheader("التجارب المحفوظة")
    experiments = load_experiments()
    
    if experiments:
        for idx, exp in enumerate(reversed(experiments), 1):
            with st.expander(f"📋 {exp['name']} - {exp['date']}"):
                st.write(f"**المكونات:** {exp['formulation']}")
                st.write(f"**النتائج:** {exp['result']}")
        
        # خيار تحميل كـ CSV
        if st.button("📥 تحميل جميع التجارب كـ Excel"):
            df = pd.DataFrame([
                {
                    "اسم التجربة": e['name'],
                    "التاريخ": e['date'],
                    "المكونات": e['formulation'],
                    "النتائج": e['result']
                }
                for e in experiments
            ])
            st.download_button(
                label="⬇️ Download Excel",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"experiments_{datetime.date.today()}.csv",
                mime="text/csv"
            )
    else:
        st.info("لا توجد تجارب محفوظة حتى الآن.")

# ==================== القسم الثالث: خلطات مقترحة ====================
with tab3:
    st.header("قاعدة بيانات الخلطات")
    
    formulations = {
        "خلطة الفلين الفضائي (Space Cork)": {
            "الوصف": "ممتازة لخفة الوزن والعزل الحراري العالي",
            "المكونات": {
                "PPG": "40%",
                "PMDI": "15%",
                "فلين مطحون": "25%",
                "ATH": "15%",
                "كيفلر": "5%"
            },
            "الميزات": ["⭐ خفيفة الوزن", "⭐ عزل حراري عالي", "⭐ سهلة الصب"]
        },
        "الخلطة السيراميكية القاسية (Ceramic Char)": {
            "الوصف": "تعتمد على المواد المتاحة حالياً",
            "المكونات": {
                "PPG": "60g",
                "زيت الخروع": "30g",
                "PMDI": "21g",
                "السيليكا": "35g",
                "كيفلر": "3g",
                "الكربون الأسود": "4g"
            },
            "الميزات": ["⭐ مقاومة عالية للحرارة", "⭐ كثافة متوسطة", "⭐ توفر المواد"]
        },
        "خلطة الطبقة الزجاجية (Glassy Layer)": {
            "الوصف": "استخدام حمض البوريك كبديل للـ ATH",
            "المكونات": {
                "PPG": "60%",
                "حمض البوريك": "20%",
                "PMDI": "15%",
                "ألياف أرامية": "5%"
            },
            "الميزات": ["⭐ طبقة زجاجية عند الحرق", "⭐ منع تسرب الأكسجين", "⭐ كثافة منخفضة"]
        }
    }
    
    selected_formulation = st.selectbox("اختر الخلطة:", list(formulations.keys()))
    
    if selected_formulation:
        form_data = formulations[selected_formulation]
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("الوصف")
            st.write(form_data["الوصف"])
            st.subheader("الميزات")
            for feature in form_data["الميزات"]:
                st.write(feature)
        
        with col2:
            st.subheader("المكونات")
            for ingredient, value in form_data["المكونات"].items():
                st.write(f"• **{ingredient}:** {value}")

# ==================== القسم الرابع: القسم التعليمي ====================
with tab4:
    st.header("دليل المختبر والاختبارات القياسية")
    
    guide_choice = st.selectbox("اختر الدليل التعليمي:", [
        "طريقة الخلط والصب",
        "اختبار اللهب (Oxy-Acetylene)",
        "اختبار الكثافة",
        "معايير الأمان"
    ])
    
    if guide_choice == "طريقة الخلط والصب":
        st.markdown("""
        ### 🔬 خطوات العمل في المختبر:
        
        #### 1️⃣ **التجفيف:**
        - ضع المواد الجافة (السيليكا، الكيفلر، إلخ) في الفرن عند **110°C** لمدة **ساعتين**
        - تأكد من إزالة الرطوبة تماماً
        
        #### 2️⃣ **المزج الأولي:**
        - اخلط البوليولات (PPG والخروع) مع الإضافات الجافة والألياف بالخلاط الميكانيكي
        - استخدم سرعة متوسطة لمدة 3-5 دقائق
        - تأكد من توزيع متساوي للألياف
        
        #### 3️⃣ **إزالة الغازات:**
        - ضع الخليط في غرفة التفريغ (Vacuum) لـ **10-15 دقيقة**
        - هدف: سحب الهواء المحبوس والرطوبة
        
        #### 4️⃣ **إضافة المصلب:**
        - أضف الـ PMDI المحسوب مسبقاً
        - اخلط بسرعة **عالية** (لمدة **دقيقة واحدة فقط**)
        - لا تتأخر في الخلط لتجنب بدء التفاعل السريع
        
        #### 5️⃣ **الصب:**
        - صب في قالب مدهون بمادة مانعة للالتصاق
        - تأكد من عدم وجود فقاعات هواء
        - ضع القالب في فرن المعالجة (Curing Oven)
        - درجة الحرارة: **60°C** لمدة **24 ساعة**
        """)
    
    elif guide_choice == "اختبار اللهب (Oxy-Acetylene)":
        st.markdown("""
        ### 🔥 خطوات اختبار التآكل الخطي:
        
        #### المعدات المطلوبة:
        - جهاز شعلة الأوكسي-أسيتيلين
        - مسطرة قياس دقيقة (±0.1 ملم)
        - حساس حرارة (Thermocouple K-type)
        - عينة بسمك 10-15 ملم
        
        #### خطوات الاختبار:
        
        1️⃣ **تحضير العينة:**
           - جهز عينة بسمك **10-15 ملم**
           - اقيس السمك الأولي بدقة
        
        2️⃣ **تثبيت الحساسات:**
           - ضع حساس حرارة (Thermocouple) خلف العينة
           - قياس درجة الحرارة المتسربة من الجانب الآخر
        
        3️⃣ **ضبط الشعلة:**
           - شغل جهاز الأوكسي-أسيتيلين
           - اضبط المسافة بين الشعلة والعينة على **1-2 سم**
           - استخدم شعلة معايرة
        
        4️⃣ **إجراء الاختبار:**
           - سلط اللهب لمدة زمنية محددة (**20-60 ثانية** حسب المعيار)
           - اترك العينة لتبرد تدريجياً
        
        5️⃣ **القياس والحساب:**
           - اقيس السمك النهائي بعد الحرق
           - **معدل التآكل (mm/s) = (السمك قبل - السمك بعد) ÷ الزمن (ثانية)**
           - سجل درجة الحرارة العظمى
        
        #### نتائج مقبولة:
        - معدل التآكل: **< 2 mm/min** (للعزلات الجيدة)
        - درجة الحرارة المتسربة: **< 200°C** (بعد التعريض 60 ثانية)
        """)
    
    elif guide_choice == "اختبار الكثافة":
        st.markdown("""
        ### ⚖️ طريقة قياس الكثافة:
        
        #### الطريقة الأولى: الترجيح المائي (Archimedes):
        
        1. **قياس الوزن:**
           - زن العينة في الهواء → **W₁** (جرام)
        
        2. **التنقيع:**
           - انقع العينة في الماء المقطر لمدة 24 ساعة
           - اسحب الهواء باستخدام التفريغ الخاص بك
        
        3. **وزن تحت الماء:**
           - زن العينة وهي مغمورة في الماء → **W₂** (جرام)
        
        4. **الحساب:**
           - الحجم = (W₁ - W₂) ÷ كثافة الماء (1 جرام/سم³)
           - **الكثافة = W₁ ÷ الحجم** (جرام/سم³)
        
        #### النطاق المتوقع:
        - العزلات الفضائية: **0.2 - 0.6 جرام/سم³**
        - العزلات السيراميكية: **0.8 - 1.2 جرام/سم³**
        """)
    
    elif guide_choice == "معايير الأمان":
        st.markdown("""
        ### ⚠️ معايير الأمان والسلامة:
        
        #### المواد الخطرة:
        - **PMDI (البوليميثيلين البوليفينيل ايزوسيانات):**
          - مسبب للربو والحساسية
          - استخدم كمامة N95 عند التعامل به
          - تهوية جيدة في المختبر
        
        - **الألياف (Aramid, Glass fibers):**
          - قد تسبب تهيج الجهاز التنفسي
          - ارتدِ قفازات وكمامة
          - تجنب استنشاق الغبار
        
        - **حمض البوريك:**
          - سام عند الابتلاع
          - ارتدِ قفازات واقية
          - اغسل يديك جيداً بعد الاستخدام
        
        #### الاحتياطات الأساسية:
        ✅ ارتدِ **بدلة حماية وقفازات وكمامة**
        ✅ استخدم **نظارات واقية** عند الاختبار بالشعلة
        ✅ تأكد من **التهوية الجيدة** في المختبر
        ✅ احفظ المواد بعيداً عن الحرارة والرطوبة
        ✅ اقرأ **بطاقات أمان المواد (SDS)** قبل الاستخدام
        ✅ استخدم **طفاية حريق** قريبة من منطقة العمل
        """)

st.markdown("---")
st.markdown("👨‍🔬 **تطبيق تم تطويره لمتخصصي الهندسة الفضائية والعوازل الحرارية**")
