import streamlit as st
import cv2
import numpy as np
import time
import base64
from gtts import gTTS
import io

def speak(text):
    """音声を再生する"""
    tts = gTTS(text=text, lang='ja')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_base64 = base64.b64encode(fp.read()).decode()
    audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    st.components.v1.html(audio_html, height=0)

def main():
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>これ、なーんだ</h1>", unsafe_allow_html=True)

    # クイズデータ
    QUIZ_DATA = [
        {"image": "banana.jpg", "answer": "バナナ"},
        {"image": "da-papa.jpg", "answer": "パパ"},
        {"image": "do-oohorisuwan.jpg", "answer": "おおほりこうえん"}
    ]

    # セッション状態の初期化
    if 'q_idx' not in st.session_state:
        st.session_state.q_idx = 0
    if 'blur' not in st.session_state:
        st.session_state.blur = 101
    if 'run' not in st.session_state:
        st.session_state.run = False
    if 'ans' not in st.session_state:
        st.session_state.ans = False

    current = QUIZ_DATA[st.session_state.q_idx]

    # ボタン配置
    col1, col2 = st.columns(2)
    with col1:
        if st.button("はじめる"):
            st.session_state.run = True
            st.session_state.ans = False
            st.session_state.blur = 101
            msg = "これどーこだ？" if current["image"].startswith("do-") else "これだーれだ？" if current["image"].startswith("da-") else "これなーんだ？"
            speak(msg)
    with col2:
        if st.button("わかった！"):
            st.session_state.run = False

    # 画像表示エリア
    area = st.empty()
    
    img = cv2.imread(current["image"])
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        st.error("画像が見つかりません")
        return

    # --- メインのアニメーション処理 ---
    if st.session_state.run and st.session_state.blur > 1:
        # 101から1まで100段階で変化
        # 0.1秒 × 100回 = 10秒
        for b in range(st.session_state.blur, 0, -1):
            if not st.session_state.run:
                st.session_state.blur = b
                break
            
            k = b if b % 2 != 0 else b + 1
            processed = cv2.GaussianBlur(img, (k, k), 0)
            area.image(processed, use_column_width=True)
            
            st.session_state.blur = b
            time.sleep(0.1) # ここで10秒になるよう調整
            
            if b <= 1:
                st.session_state.run = False
                st.rerun()
    else:
        # 停止中
        k = st.session_state.blur if st.session_state.blur % 2 != 0 else st.session_state.blur + 1
        disp = cv2.GaussianBlur(img, (k, k), 0) if k > 1 else img
        area.image(disp, use_column_width=True)

    # ⑤ 「こたえ」ボタン
    if st.button("こたえ"):
        st.session_state.ans = True

    if st.session_state.ans:
        st.markdown(f"<h2 style='text-align: center; color: #E74C3C;'>正解は： {current['answer']}</h2>", unsafe_allow_html=True)
        if st.session_state.q_idx < len(QUIZ_DATA) - 1:
            if st.button("つぎの問題へ"):
                st.session_state.q_idx += 1
                st.session_state.blur = 101
                st.session_state.ans = False
                st.session_state.run = False
                st.rerun()
        else:
            st.balloons()
            if st.button("最初に戻る"):
                st.session_state.q_idx = 0
                st.rerun()

if __name__ == "__main__":
    main()
