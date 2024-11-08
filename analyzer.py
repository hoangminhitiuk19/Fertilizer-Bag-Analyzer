import time
import easyocr
import re
import cv2
import streamlit as st
from PIL import Image
from gtts import gTTS
import io
import numpy as np
import base64
import speech_recognition as sr 
import winsound

number_word_map = {
    "một": 1, "hai": 2, "ba": 3, "bốn": 4, "năm": 5, "sáu": 6,
    "bảy": 7, "tám": 8, "chín": 9, "mười": 10, "mười một": 11,
    "mười hai": 12, "mười ba": 13, "mười bốn": 14, "mười lăm": 15
    # Add more mappings as needed
}

def convert_vietnamese_number_to_int(vietnamese_number):
    vietnamese_number = vietnamese_number.strip().lower()
    if vietnamese_number in number_word_map:
        return number_word_map[vietnamese_number]
    else:
        try:
            return int(vietnamese_number)
        except ValueError:
            return None

def play_beep():
    winsound.Beep(1000, 500)


def extract_npk_from_image(image_data):
    reader = easyocr.Reader(['en'], gpu=True, verbose=False)
    image = np.array(Image.open(image_data))
    height, width = image.shape[:2]

    if width > height:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    result = reader.readtext(image, detail=0)
    full_text = ' '.join(result)
    match = re.search(r'\b(\d+)-(\d+)-(\d+)\b', full_text)

    if match:
        n, p, k = match.groups()
        return int(n), int(p), int(k)
    else:
        return None

def speak_vietnamese(text):
    tts = gTTS(text, lang='vi')  
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    audio_base64 = base64.b64encode(audio_buffer.read()).decode("utf-8")
    audio_html = f"""
        <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    
def extract_quantity(text):
    match = re.search(r'\bmua\b.*?(\d+)\s*', text, re.IGNORECASE)
    if match:
        quantity = int(match.group(1))
        return quantity
    
    words = text.split()
    for word in words:
        quantity = convert_vietnamese_number_to_int(word)
        if quantity is not None:
            return quantity
    
    return None

def listen_to_user():
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=2) as source:
        st.write("Đang lắng nghe...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
        st.write("Đã nghe, đang xử lý...")
    try:
        text = recognizer.recognize_google(audio, language="vi-VN")
        st.write(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.write("Could not understand the audio.")
        return None
    except sr.RequestError as e:
        st.write(f"Error with the speech recognition service: {e}")
        return None

def hear_user_input():
    user_input = listen_to_user()
    
    if user_input is None:
        st.write("Please say the quantity again.")
        return None

    quantity = extract_quantity(user_input)
    
    if quantity is None:
        st.write("Không nhận diện được số lượng. Vui lòng nói lại theo mẫu 'tôi mua [số lượng] túi'.")
        speak_vietnamese("Không nhận diện được số lượng. Vui lòng nói lại theo mẫu 'tôi mua [số lượng] túi'.")
        time.sleep(8)
        play_beep()
        return None
    
    return quantity

def confirm_quantity(quantity):
    while True:
        confirmation_text = f"Bạn muốn mua {quantity} túi phải không? Nếu đúng, hãy nói 'Đúng rồi', nếu sai, hãy nói 'Sai rồi'."
        speak_vietnamese(confirmation_text)
        time.sleep(8)
        play_beep() 
        
        start_time = time.time()
        confirmation_response = None
        
        while time.time() - start_time < 10:
            confirmation_response = listen_to_user()
            if confirmation_response:
                break
            
        if confirmation_response:
            if "đúng rồi" in confirmation_response.lower():
                speak_vietnamese(f"Mua {quantity} túi")
                time.sleep(2) 
                return quantity 

            elif "sai rồi" in confirmation_response.lower():
                speak_vietnamese("Sai rồi! Xin vui lòng nói lại số lượng.")
                time.sleep(4)
                play_beep()
                return False 

            else:
                st.write("Không rõ câu trả lời. Vui lòng trả lời 'Đúng rồi' hoặc 'Sai rồi'.")
                speak_vietnamese("Không rõ câu trả lời. Vui lòng trả lời 'Đúng rồi' hoặc 'Sai rồi'.")
                time.sleep(3)
                play_beep()
        else:
            st.write("Không nghe thấy câu trả lời. Vui lòng nói lại.")
            speak_vietnamese("Không nghe thấy câu trả lời. Vui lòng nói lại.")
            time.sleep(3)
            play_beep()

def process_purchase_request():
    while True:
        quantity = hear_user_input()
        
        if quantity:
            result = confirm_quantity(quantity)
            if result:
                return f"{result} túi"
            else:
                continue

st.set_page_config(
    page_title="Xác Định Giá Trị Phân Bón NPK", 
    page_icon="🧪",
    layout="centered"
)
# Streamlit app setup
st.title("Xác Định Giá Trị Phân Bón NPK")
st.write("Hãy tải lên hình ảnh bao phân bón để xác định giá trị NPK.")

# File upload
uploaded_file = st.file_uploader("Chọn hình ảnh...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Hình ảnh đã tải lên", use_container_width=True)

    npk_values = extract_npk_from_image(uploaded_file)

    if npk_values:
        n, p, k = npk_values
        result_text = f"Giá trị NPK: N={n}%, P={p}%, K={k}%"
        st.write(result_text)
        speak_vietnamese(result_text)
        time.sleep(9)
        speak_vietnamese("Hãy nói sau tiếng bíp")
        time.sleep(2)
        speak_vietnamese("Bạn muốn mua bao nhiêu túi?")
        time.sleep(3)
        play_beep() 
        result = process_purchase_request()
        st.write(f"Số lượng: {result}")
    else:
        st.write("Không tìm thấy NPK.")
        speak_vietnamese("Không tìm thấy giá trị NPK.")


