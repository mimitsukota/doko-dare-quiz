import streamlit as st
import cv2
import numpy as np
import time
import base64
from gtts import gTTS
import io
import random

def speak(text):
    """音声を再生する関数"""
    tts = gTTS(text=text, lang='ja')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_base64 = base64.b64encode(fp.read()).decode()
    audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    st.components.v1.html(audio_html, height=0)

def main():
    # タイトル
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>これ、なーんだ</h1>", unsafe_allow_html=True)

    # クイズデータ（全35問）
    QUIZ_DATA = [
        {"image": "banana.jpg", "answer": "バナナ"},
        {"image": "da-papa.jpg", "answer": "パパ"},
        {"image": "do-oohorisuwan.jpg", "answer": "おおほりこうえん"},
        {"image": "azarashi.jpg", "answer": "アザラシ"},
        {"image": "bus.jpg", "answer": "バス"},
        {"image": "chikatetsu.jpg", "answer": "ちかてつ"},
        {"image": "da-dare1.jpg", "answer": "だれ？"},
        {"image": "da-dare2.jpg", "answer": "だれ？"},
        {"image": "da-dare3.jpg", "answer": "だれ？"},
        {"image": "da-dare4.jpg", "answer": "だれ？"},
        {"image": "da-feretto.jpg", "answer": "フェレット"},
        {"image": "da-mamatotougo.jpg", "answer": "ママととうご"},
        {"image": "da-mitsuki.jpg", "answer": "みつき"},
        {"image": "da-obaketogo.jpg", "answer": "おばけとうご"},
        {"image": "da-pengintogo.jpg", "answer": "ペンギンとうご"},
        {"image": "da-surakkusu.jpg", "answer": "スラックスさん"},
        {"image": "densya.jpg", "answer": "でんしゃ"},
        {"image": "do-oohoriike.jpg", "answer": "おおほりこうえん"},
        {"image": "do-uminaka.jpg", "answer": "うみのなかみち"},
        {"image": "fIghtakun.jpg", "answer": "ファイタくん"},
        {"image": "do-junglia.jpg", "answer": "ジャングリア"},
        {"image": "da-nasuba.jpg", "answer": "ナスバちゃん"},
        {"image": "rama.jpg", "answer": "ラマ"},
        {"image": "da-setsubun.jpg", "answer": "おに"},
        {"image": "da-tereby.jpg", "answer": "テレビーくん"},
        {"image": "da-togobaby.jpg", "answer": "うまれたてとうご"},
        {"image": "do-kankoku.jpg", "answer": "かんこく"},
        {"image": "do-malinworld.jpg", "answer": "マリンワールド"},
        {"image": "do-hachirogaura.jpg", "answer": "かめちゃんいけ"},
        {"image": "do-zoo.jpg", "answer": "どうぶつえん"},
        {"image": "do-doko1.jpg", "answer": "どこ？"},
        {"image": "do-jyang2.jpg", "answer": "ジャングリア"},
        {"image": "do-iki1.jpg", "answer": "いき"},
        {"image": "do-inn.jpg", "answer": "インザパーク"},
        {"image": "da-hadakatogo.jpg", "answer": "はだかんぼとうご"}
    ]

    # アプリの状態管理（セッション）
    if 'q_idx' not in st.session_state:
        st.session_state.q_idx = random.randint(0, len(QUIZ_DATA) - 1)
    if 'blur' not in st.session_state:
        st.session_state.blur = 101
    if 'run' not in st.session_state:
        st.session_state.run = False
    if 'ans' not in st.session_state:
        st.session_state.ans = False

    current = QUIZ_DATA[st.session_state.q_idx]

    # 操作ボタン
    col1, col2 = st.columns(2)
    with col1:
        if st.button("はじめる"):
            st.session_state.run = True
            st.session_state.ans = False
            st.session_state.blur = 101
            # 音声の出し分け
            filename = current["image"]
            msg = "これどーこだ？" if filename.startswith("do-") else "これだーれだ？" if filename.startswith("da-") else "これなーんだ？"
            speak(msg)
    with col2:
        if st.button("わかった！"):
            st.session_state.run = False

    # 画像の表示エリア
    area = st.empty()
    img = cv2.imread(current["image"])
    
    if img is not None:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # じわじわ変化させる処理
        if st.session_state.run and st.session_state.blur > 1:
            for b in range(st.session_state.blur, 0, -1):
                if not st.session_state.run:
                    st.session_state.blur = b
                    break
                
                k = b if b % 2 != 0 else b + 1
                processed = cv2.GaussianBlur(img, (k, k), 0)
                area.image(processed, use_column_width=True)
                
                st.session_state.blur = b
                time.sleep(0.1)
                
                if b <= 1:
                    st.session_state.run = False
                    st.rerun()
        else:
            # 停止中または終了後の表示
            k = st.session_state.blur if st.session_state.blur % 2 != 0 else st.session_state.blur + 1
            disp = cv2.GaussianBlur(img, (k, k), 0) if k > 1 else img
            area.image(disp, use_column_width=True)
    else:
        st.error(f"がぞう「{current['image']}」が見つかりません。GitHubを確認してね。")

    # こたえ合わせ
    if st.button("こたえ"):
        st.session_state.ans = True

    if st.session_state.ans:
        st.markdown(f"<h2 style='text-align: center; color: #E74C3C;'>こたえは： {current['answer']}</h2>", unsafe_allow_html=True)
        
        if st.button("つぎのもんだいへ"):
            st.session_state.q_idx = random.randint(0, len(QUIZ_DATA) - 1)
            st.session_state.blur = 101
            st.session_state.ans = False
            st.session_state.run = False
            st.rerun()

if __name__ == "__main__":
    main()
