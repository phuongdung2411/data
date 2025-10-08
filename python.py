import streamlit as st
from google import genai
from google.genai import types

# 🚨 CHÚ Ý QUAN TRỌNG:
# 1. Bạn cần cài đặt thư viện: pip install google-genai streamlit
# 2. Đặt API key của bạn vào Streamlit Secrets (tên là "GEMINI_API_KEY") 
#    hoặc vào biến môi trường. Đoạn mã này sẽ tự động lấy từ st.secrets.

# --- CẤU HÌNH BAN ĐẦU ---

# Khởi tạo Client của Gemini
try:
    # Lấy API Key từ Streamlit Secrets
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Lỗi: Không tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")
    else:
        client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Lỗi khi khởi tạo Gemini Client: {e}")
    st.stop() # Dừng ứng dụng nếu không thể khởi tạo

MODEL_NAME = 'gemini-2.5-flash' # Mô hình mạnh mẽ và tối ưu chi phí

# --- HÀM XỬ LÝ LOGIC ---

# Hàm khởi tạo hoặc lấy đối tượng chat
def get_chat_session():
    """Khởi tạo hoặc trả về đối tượng Chat Session từ Gemini."""
    if "chat_session" not in st.session_state:
        # Khởi tạo một đối tượng chat mới
        st.session_state.chat_session = client.chats.create(
            model=MODEL_NAME
            # Bạn có thể thêm cấu hình system_instruction tại đây nếu muốn
            # system_instruction="Bạn là một trợ lý ảo thân thiện và hữu ích."
        )
        st.session_state.messages = [] # Lưu trữ lịch sử tin nhắn
    return st.session_state.chat_session

# --- KHỞI TẠO VÀ HIỂN THỊ KHUNG CHAT ---

st.title("🤖 Chatbot Gemini trên Streamlit")
st.caption(f"Sử dụng mô hình: **{MODEL_NAME}**")

# Lấy/khởi tạo session chat
chat = get_chat_session()

# Hiển thị lịch sử tin nhắn
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["content"])

# --- Ô NHẬP LIỆU (Chat Input) ---

# Xử lý khi người dùng nhập tin nhắn
if prompt := st.chat_input("Hỏi Gemini bất cứ điều gì..."):
    # 1. Hiển thị tin nhắn của người dùng
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Lưu tin nhắn của người dùng vào lịch sử
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Gửi tin nhắn đến Gemini và hiển thị phản hồi
    with st.chat_message("assistant"):
        # Gửi tin nhắn và nhận phản hồi
        # Sử dụng stream=True để hiển thị phản hồi theo thời gian thực (hiện đại hơn)
        with st.spinner("Gemini đang trả lời..."):
            try:
                # Gửi tin nhắn (prompt) tới phiên chat
                response = chat.send_message(prompt, stream=True)
                
                # Tạo một placeholder để viết câu trả lời từng phần
                full_response = ""
                message_placeholder = st.empty()
                
                for chunk in response:
                    # Nối các phần nội dung nhận được
                    full_response += chunk.text
                    # Cập nhật placeholder với nội dung đã nối
                    message_placeholder.markdown(full_response + "▌") # Thêm con trỏ nhấp nháy

                # Cập nhật lại với nội dung hoàn chỉnh
                message_placeholder.markdown(full_response)
                
                # 3. Lưu phản hồi vào lịch sử
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_message = f"Đã xảy ra lỗi khi giao tiếp với Gemini: {e}"
                st.error(error_message)
                # Nếu có lỗi, có thể xóa tin nhắn cuối cùng của người dùng để họ thử lại
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                    st.session_state.messages.pop()

# --- KHU VỰC
