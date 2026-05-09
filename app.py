import streamlit as st
import cv2
import numpy as np
import time
import base64
import os

# --- 音声再生用の関数 ---
def play_audio(text):
    """
    ブラウザで音声を自動再生するためのHTMLを生成する
    ※本来は音声ファイル(mp3等)を用意するのがベストですが、
    ここでは以前のプロジェクトのように、まずはテキスト表示と擬似再生の枠組みを作ります。
    もしmp3ファイルがある場合は、そのファイルを読み込む処理に書き換え可能です。
    """
    # 今回は簡略化のため、画面に大きくメッセージを出す形式にしています
    st.markdown(f"### 🔊 {text}")

def main():
    # ① タイトル
    st.markdown("<h1 style='text-align: center;'>これ、なーんだ</h1>", unsafe_allow_html=True)

    # クイズデータ（画像ファイル名と正解）
    QUIZ_DATA = [
        {"image": "banana.jpg", "answer": "バナナ"},
        {"image": "da-papa.jpg", "answer": "パパ"},
        {"image": "do-oohorisuwan.jpg", "answer": "おおほりこうえん"}
    ]

    # セッション状態の管理
    if 'q_idx' not in st.session_state:
        st.session_state.q_idx = 0
    if 'blur_level' not in st.session_state:
        st.session_state.blur_level = 100
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
        st.session_state.blur_level = 100
        
        # ファイル名による音声（テキスト）の分岐
        if filename.startswith("do-"):
            audio_text = "これどーこだ？"
        elif filename.startswith("da-"):
            audio_text = "これだーれだ？"
        else:
            audio_text = "これなーんだ？"
            
        play_audio(audio_text)

    # 画像表示エリア
    placeholder = st.empty()
    
    # 画像の読み込み
    img = cv2.imread(filename)
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        st.error(f"画像 {filename} が見つかりません。")
        return

    # ③ ぼかしアニメーション（約10秒）
    if st.session_state.is_running and st.session_state.blur_level > 1:
        for b in range(st.session_state.blur_level, 0, -2):
            if not st.session_state.is_running:
                st.session_state.blur_level = b
                break
            
            k = b if b % 2 != 0 else b + 1
            processed_img = cv2.GaussianBlur(img, (k, k), 0)
            placeholder.image(processed_img, use_column_width=True)
            
            st.session_state.blur_level = b
            time.sleep(0.2) # 0.2秒 × 50回 = 10秒
            
            if b <= 1:
                st.session_state.is_running = False
    else:
        k = st.session_state.blur_level if st.session_state.blur_level % 2 != 0 else st.session_state.blur_level + 1
        display_img = cv2.GaussianBlur(img, (k, k), 0) if k > 1 else img
        placeholder.image(display_img, use_column_width=True)

    # ④ 「わかった！」ボタン
    if st.button("わかった！"):
        st.session_state.is_running = False

    # ⑤ 「こたえ」ボタン
    if st.button("こたえ"):
        st.session_state.show_ans = True

    if st.session_state.show_ans:
        st.success(f"こたえは： **{current_quiz['answer']}**")
        
        if st.session_state.q_idx < len(QUIZ_DATA) - 1:
            if st.button("つぎの問題へ"):
                st.session_state.q_idx += 1
                st.session_state.blur_level = 100
                st.session_state.show_ans = False
                st.rerun()
        else:
            st.balloons()
            if st.button("最初に戻る"):
                st.session_state.q_idx = 0
                st.rerun()

if __name__ == "__main__":
    main()
