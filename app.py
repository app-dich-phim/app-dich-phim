import os
import tempfile
import streamlit as st
import moviepy.editor as mp
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS

st.set_page_config(page_title="App Dịch & Lồng Tiếng Phim", page_icon="🎬", layout="centered")

st.title("🎬 Ứng dụng Dịch & Lồng Tiếng Video")
st.write("Tải lên video ngắn (.mp4) để nhận dạng tiếng Anh, dịch sang tiếng Việt và lồng tiếng mới.")

uploaded_file = st.file_uploader("Chọn video từ thiết bị của bạn", type=["mp4"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    if st.button("Bắt đầu xử lý"):
        with st.spinner("Đang trích xuất và xử lý âm thanh..."):
            try:
                # Lưu file video tạm thời
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
                    tmp_video.write(uploaded_file.read())
                    video_path = tmp_video.name

                # Trích xuất âm thanh từ video
                video = mp.VideoFileClip(video_path)
                audio_path = video_path.replace('.mp4', '.wav')
                video.audio.write_audiofile(audio_path, logger=None)

                # 1. Nhận dạng giọng nói (ASR)
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio_data = recognizer.record(source)
                
                text_src = recognizer.recognize_google(audio_data, language="en-US")
                st.subheader("1. Văn bản nhận dạng (Tiếng Anh):")
                st.info(text_src)

                # 2. Dịch văn bản (Translation)
                translator = Translator()
                translated = translator.translate(text_src, dest='vi')
                text_vi = translated.text
                st.subheader("2. Văn bản đã dịch (Tiếng Việt):")
                st.success(text_vi)

                # 3. Tạo giọng đọc lồng tiếng (TTS)
                tts = gTTS(text=text_vi, lang='vi')
                tts_audio_path = video_path.replace('.mp4', '_tts.mp3')
                tts.save(tts_audio_path)

                # 4. Khớp/Gộp âm thanh mới vào video
                new_audio = mp.AudioFileClip(tts_audio_path)
                final_video = video.set_audio(new_audio)
                
                output_path = video_path.replace('.mp4', '_dubbed.mp4')
                final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)

                st.subheader("3. Video sau khi lồng tiếng thành công:")
                st.video(output_path)
                
                # Dọn dẹp tài nguyên
                video.close()
                new_audio.close()
                final_video.close()

            except Exception as e:
                st.error(f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}")
