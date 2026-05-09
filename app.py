import streamlit as st
import cv2
import numpy as np
import time
import base64

# --- クイズデータの設定 ---
# ファイル名から正解を推測して設定しています。適宜修正してください。
QUIZ_DATA = [
    {"image": "banana.jpg", "answer": "ばなな"},
    {"image": "da-papa.jpg", "answer": "おとうさん"},
    {"image": "do-oohorisuwan.jpg", "answer": "おおほりこうえんのスワン"}
]

def get_audio_text(filename):
    """ファイル名に応じて読み上げテキストと音声ファイルを判定する"""
    if filename.startswith("do-"):
        return "これどーこだ？"
    elif filename.startswith("da-"):
        return "これだーれだ？"
    else:
        return "これなーんだ？"

def main():
    # ① タイトル
    st.markdown("<h1 style='text-align: center;'>これ、なーんだ</h1>", unsafe_allow_html=True)

    # セッション状態の初期化
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
    audio_text = get_audio_text(filename)

    # ② 「はじめる」ボタン
    if st.button("はじめる"):
        st.session_state.is_running = True
        st.session_state.show_ans = False
        st.session_state.blur_level = 100
        # 音声の表示（実際にはここに音声再生ロジックが入ります）
        st.subheader(f"🔊 {audio_text}")

    # 画像表示エリア
    placeholder = st.empty()
    
    # 画像の読み込み
    img = cv2.imread(filename)
    if img is None:
        st.error(f"画像 {filename} が見つかりません。")
        return
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # ③ ぼかしアニメーション
    if st.session_state.is_running and st.session_state.blur_level > 1:
        # 約10秒かけて鮮明にする（ループ回数とsleepで調整）
        for b in range(st.session_state.blur_level, 0, -2):
            if not st.session_state.is_running:
                st.session_state.blur_level = b
                break
            
            k = b if b % 2 != 0 else b + 1
            processed_img = cv2.GaussianBlur(img, (k, k), 0)
            placeholder.image(processed_img, use_column_width=True)
            
            st.session_state.blur_level = b
            time.sleep(0.2) 
            
            if b <= 1:
                st.session_state.is_running = False
    else:
        # 停止中または完了後の表示
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
        
        # 次の問題へのナビゲーション
        if st.session_state.q_idx < len(QUIZ_DATA) - 1:
            if st.button("つぎの問題へ"):
                st.session_state.q_idx += 1
                st.session_state.blur_level = 100
                st.session_state.show_ans = False
                st.rerun()
        else:
            st.balloons()
            st.write("全問終了です！")
            if st.button("最初に戻る"):
                st.session_state.q_idx = 0
                st.rerun()

if __name__ == "__main__":
    main()