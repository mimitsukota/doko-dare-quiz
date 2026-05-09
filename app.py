import streamlit as st
import cv2
import numpy as np
import base64
from gtts import gTTS
import io

def speak(text):
    tts = gTTS(text=text, lang='ja')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_base64 = base64.b64encode(fp.read()).decode()
    audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    st.components.v1.html(audio_html, height=0)

def get_image_base64(img):
    _, buffer = cv2.imencode(".jpg", img)
    return base64.b64encode(buffer).decode()

def main():
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>これ、なーんだ</h1>", unsafe_allow_html=True)

    QUIZ_DATA = [
        {"image": "banana.jpg", "answer": "バナナ"},
        {"image": "da-papa.jpg", "answer": "パパ"},
        {"image": "do-oohorisuwan.jpg", "answer": "おおほりこうえん"}
    ]

    if 'q_idx' not in st.session_state:
        st.session_state.q_idx = 0
    if 'show_ans' not in st.session_state:
        st.session_state.show_ans = False

    current_quiz = QUIZ_DATA[st.session_state.q_idx]
    filename = current_quiz["image"]

    # 画像の読み込み
    img = cv2.imread(filename)
    if img is None:
        st.error(f"画像 {filename} が見つかりません。")
        return
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # パラパラ漫画用の画像を30枚作成（モザイク）
    img_list = []
    ratios = np.linspace(0.01, 1.0, 30)
    for r in ratios:
        h, w = img.shape[:2]
        small = cv2.resize(img, None, fx=r, fy=r, interpolation=cv2.INTER_NEAREST)
        mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        img_list.append(get_image_base64(mosaic))

    img_json = str(img_list).replace("'", '"')

    # ボタンの配置
    col1, col2 = st.columns(2)
    with col1:
        if st.button("はじめる"):
            msg = "これどーこだ？" if filename.startswith("do-") else "これだーれだ？" if filename.startswith("da-") else "これなーんだ？"
            speak(msg)
            # はじめるボタンを押したときにJSに通知
            st.components.v1.html(f"""
                <script>
                window.parent.postMessage({{type: 'start'}}, '*');
                </script>
            """, height=0)

    with col2:
        if st.button("わかった！"):
             st.components.v1.html(f"""
                <script>
                window.parent.postMessage({{type: 'stop'}}, '*');
                </script>
            """, height=0)

    # メインの画像表示とアニメーション（JavaScript）
    html_code = f"""
    <div style="text-align:center;">
        <img id="quiz-img" src="data:image/jpeg;base64,{img_list[0]}" style="width:100%; border-radius:10px;">
    </div>
    <script>
        var images = {img_json};
        var currentIndex = 0;
        var intervalId = null;
        var imgElement = document.getElementById('quiz-img');

        window.addEventListener('message', function(event) {{
            if (event.data.type === 'start') {{
                currentIndex = 0;
                if(intervalId) clearInterval(intervalId);
                intervalId = setInterval(function() {{
                    if (currentIndex < images.length - 1) {{
                        currentIndex++;
                        imgElement.src = "data:image/jpeg;base64," + images[currentIndex];
                    }} else {{
                        clearInterval(intervalId);
                    }}
                }}, 333); // 30枚を約10秒で回す (10000ms / 30)
            }} else if (event.data.type === 'stop') {{
                clearInterval(intervalId);
            }}
        }});
        
        // 画像クリックで再開
        imgElement.onclick = function() {{
            if(intervalId) clearInterval(intervalId);
            intervalId = setInterval(function() {{
                if (currentIndex < images.length - 1) {{
                    currentIndex++;
                    imgElement.src = "data:image/jpeg;base64," + images[currentIndex];
                }} else {{
                    clearInterval(intervalId);
                }}
            }}, 333);
        }};
    </script>
    """
    st.components.v1.html(html_code, height=400)

    # ⑤ 「こたえ」ボタン
    if st.button("こたえ"):
        st.session_state.show_ans = True

    if st.session_state.show_ans:
        st.markdown(f"<h2 style='text-align: center; color: #E74C3C;'>正解は： {current_quiz['answer']}</h2>", unsafe_allow_html=True)
        if st.session_state.q_idx < len(QUIZ_DATA) - 1:
            if st.button("つぎの問題へ"):
                st.session_state.q_idx += 1
                st.session_state.show_ans = False
                st.rerun()
        else:
            st.balloons()
            if st.button("最初に戻る"):
                st.session_state.q_idx = 0
                st.rerun()

if __name__ == "__main__":
    main()
