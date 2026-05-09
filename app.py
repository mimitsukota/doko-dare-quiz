import streamlit as st
import cv2
import numpy as np
import time
import base64
from gtts import gTTS
import io

def speak(text):
    """テキストを音声に変換してブラウザで再生する"""
    tts = gTTS(text=text, lang='ja')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_base64 = base64.b64encode(fp.read()).decode()
    audio_html = f"""
        <audio autoplay="true">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(audio_html, height=0)

def main():
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>これ、なーんだ</h1>", unsafe_allow_html=True)

    QUIZ_DATA = [
        {"image": "banana.jpg", "answer": "バナナ"},
        {"image": "da-papa.jpg", "answer": "パパ"},
        {"image": "do-oohorisuwan.jpg", "answer": "おおほりこうえん"}
    ]

    if 'q_idx' not in st.session_state:
        st.session_state.q_idx = 0
    if 'blur_level' not in st.session_state:
        st.session_state.blur_level = 161
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'show_ans' not in st.session_state:
        st.session_state.show_ans = False

    current_quiz = QUIZ_DATA[st.session_state.q_idx]
    filename = current_quiz["image"]

    # ② 「はじめる」ボタン
    if st.button("はじめる"):
        st.session_state.is_running = True
        st.session_state.show_ans = False
        st.session_state.blur_level = 161
        
        if filename.startswith("do-"):
            msg = "これどーこだ？"
        elif filename.startswith("da-"):
            msg = "これだーれだ？"
        else:
            msg = "これなーんだ？"
        speak(msg)

    placeholder = st.empty()
    
    img = cv2.imread(filename)
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        st.error(f"画像 {filename} が見つかりません。")
        return

    # ③ ぼかしアニメーション（より細かく、より多く書き換え）
    if st.session_state.is_running and st.session_state.blur_level > 1:
        # 161から1まで、あえて「1ずつ」減らすように変更
        # ループ回数を増やし、待機時間を極めて短くして、じわじわ感を出す
        for b in range(st.session_state.blur_level, 0, -1):
            if not st.session_state.is_running:
                st.session_state.blur_level = b
                break
            
            # ぼかし強度は必ず「奇数」である必要があるため計算
            k = b if b % 2 != 0 else b + 1
            processed_img = cv2.GaussianBlur(img, (k, k), 0)
            
            # 画像を表示
            placeholder.image(processed_img, use_column_width=True)
            
            st.session_state.blur_level = b
            # 0.05秒〜0.08秒程度の短い間隔で更新
            time.sleep(0.06) 
            
            if b <= 1:
                st.session_state.is_running = False
                st.session_state.blur_level = 1
                st.rerun()
    else:
        k = st.session_state.blur_level if st.session_state.blur_level % 2 != 0 else st.session_state.blur_level + 1
        display_img = cv2.GaussianBlur(img, (k, k), 0) if k > 1 else img
        
        # 停止中に再開するための隠しボタン的な役割
        if st.session_state.blur_level > 1 and not st.session_state.is_running:
             if st.button("▶ つづきから動かす", key="resume_img"):
                 st.session_state.is_running = True
                 st.rerun()

        placeholder.image(display_img, use_column_width=True)

    # ④ 「わかった！」ボタン
    if st.button("わかった！"):
        st.session_state.is_running = False

    # ⑤ 「こたえ」ボタン
    if st.button("こたえ"):
        st.session_state.show_ans = True

    if st.session_state.show_ans:
        st.markdown(f"<h2 style='text-align: center; color: #E74C3C;'>正解は： {current_quiz['answer']}</h2>", unsafe_allow_html=True)
        
        if st.session_state.q_idx < len(QUIZ_DATA) - 1:
            if st.button("つぎの問題へ"):
                st.session_state.q_idx += 1
                st.session_state.blur_level = 161
                st.session_state.show_ans = False
                st.session_state.is_running = False
                st.rerun()
        else:
            st.balloons()
            if st.button("最初に戻る"):
                st.session_state.q_idx = 0
                st.rerun()

if __name__ == "__main__":
    main()
    
