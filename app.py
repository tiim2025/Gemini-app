import streamlit as st
import google.generativeai as genai

# --- إعداد الصفحة ---
st.set_page_config(page_title="Gemini 3 Master App", layout="centered")

# --- القائمة الجانبية: إعدادات الأنماط ---
with st.sidebar:
    st.header("🎮 لوحة التحكم")
    api_key = st.text_input("Gemini API Key", type="password")
    
    # هنا مربط الفرس: اختيار "النمط" بدلاً من مجرد النموذج
    mode = st.radio(
        "اختر نمط العمل (Mode):",
        ["💬 Chat (العادي)", 
         "🧠 Deep Thinking (تفكير عميق)", 
         "🌍 Deep Research (بحث عميق)", 
         "📝 Canvas (برمجة/كتابة)"]
    )

# --- تعريف تعليمات النظام (System Instructions) ---
# هذه هي "الأدمغة" المختلفة التي ستبدل بينها
system_prompts = {
    "💬 Chat (العادي)": """
        أنت مساعد ذكي ومفيد. أجب باختصار ووضوح.
    """,
    
    "🧠 Deep Thinking (تفكير عميق)": """
        ACT AS A REASONING ENGINE.
        Do not answer immediately. You must use "Chain of Thought" reasoning.
        1. Break the user's problem into small logical steps.
        2. Analyze each step critically.
        3. Verify your assumptions.
        4. Finally, provide the solution based on this deep analysis.
        Show your reasoning process clearly.
    """,
    
    "🌍 Deep Research (بحث عميق)": """
        ACT AS A SENIOR ACADEMIC RESEARCHER.
        Your goal is to provide comprehensive, fact-based reports.
        - Prioritize accuracy over speed.
        - Cite sources/references for your claims.
        - If the topic is scientific (e.g., Petrophysics), use technical terminology correctly.
        - Compare different viewpoints.
    """,
    
    "📝 Canvas (برمجة/كتابة)": """
        ACT AS A SENIOR PYTHON DEVELOPER & TECHNICAL WRITER.
        - Focus on generating production-ready code.
        - Do not use conversational fillers (like "Here is the code").
        - Output clean, commented code blocks.
        - If asked to write text, use structured Markdown with headers and bullet points.
    """
}

# --- تشغيل التطبيق ---
st.title(f"Gemini 3: {mode}")

if api_key:
    # 1. تهيئة النموذج مع "التعليمات الخاصة بالنمط المختار"
    genai.configure(api_key=api_key)
    
    # اختيار التعليمات المناسبة من القاموس
    current_instruction = system_prompts[mode]
    
    # بناء النموذج مع التعليمات (System Instruction)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro", # نستخدم أقوى نموذج دائماً
        system_instruction=current_instruction 
    )

    # 2. واجهة الشات
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("أدخل أمرك هنا..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                
                # إرسال الرسالة (لاحظ أننا لا نحتاج لإرسال البرومبت الخفي كل مرة، لأنه تم تعريف النموذج به)
                # نقوم بتحويل تاريخ المحادثة للصيغة التي يفهمها النموذج
                chat = model.start_chat(history=[]) 
                
                # (ملاحظة: لتبسيط الكود هنا لم ننقل كل الهيستوري، لكن في التطبيق الكامل يجب نقلها)
                response = chat.send_message(prompt, stream=True)
                
                full_text = ""
                for chunk in response:
                    if chunk.text:
                        full_text += chunk.text
                        response_placeholder.markdown(full_text + "▌")
                
                response_placeholder.markdown(full_text)
                
            st.session_state.messages.append({"role": "assistant", "content": full_text})

        except Exception as e:
            st.error(f"حدث خطأ: {e}")
