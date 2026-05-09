import streamlit as st
import cv2
import numpy as np
import time
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

def apply_mosaic(img, ratio):
    """画像にモザイクをかける関数 (ratio: 0.01〜1.0)"""
    h, w = img.shape[:2]
    # 一度小さくしてから、元のサイズに拡大することでモザイクを作る
    small = cv2.resize(img, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

def main():
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>これ、なーんだ</h1>", unsafe_allow_html=True)

    QUIZ_DATA = [
        {"image": "banana.jpg", "answer": "バナナ"},
        {"image": "da-papa.jpg", "answer": "パパ"},
        {"image": "do-oohorisuwan.jpg", "answer": "おおほりこうえん"}
    ]

    if 'q_idx' not in st.session_state:
        st.session_state.q_idx = 0
    if 'mosaic_ratio' not in st.session_state:
        st.session_state.mosaic_ratio = 0.01  # 1%の粗さから開始
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
        st.session_state.mosaic_ratio = 0.01
        
        msg = "これどーこだ？" if filename.startswith("do-") else "これだーれだ？" if filename.startswith("da-") else "これなーんだ？"
        speak(msg)

    placeholder = st.empty()
    
    img = cv2.imread(filename)
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        st.error(f"画像 {filename} が見つかりません。")
        return

    # ③ モザイクアニメーション
    if st.session_state.is_running and st.session_state.mosaic_ratio < 1.0:
        # 0.01 (粗い) から 1.0 (鮮明) まで、じわじわ増やす
        # ステップ数を増やして10秒に調整
        steps = np.linspace(st.session_state.mosaic_ratio, 1.0, 60) 
        for r in steps:
            if not st.session_state.is_running:
                st.session_state.mosaic_ratio = r
                break
            
            mosaic_img = apply_mosaic(img, r)
            placeholder.image(mosaic_img, use_column_width=True)
            
            st.session_state.mosaic_ratio = r
            time.sleep(0.16) # 0.16秒 × 60回 ＝ 約10秒
            
            if r >= 1.0:
                st.session_state.is_running = False
                st.rerun()
    else:
        # 停止中または完了後の表示
        display_img = apply_mosaic(img, st.session_state.mosaic_ratio)
        if st.session_state.mosaic_ratio < 1.0 and not st.session_state.is_running:
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
                st.session_state.mosaic_ratio = 0.01
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
