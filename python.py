# python.py

import streamlit as st
import pandas as pd
from google import genai
@@ -11,7 +9,7 @@
layout="wide"
)

st.title("Ứng dụng Phân Tích Báo Cáo Tài Chính 📊")
st.title("Ứng dụng Phân Tích Báo Cáo Tài chính 📊")

# --- Hàm tính toán chính (Sử dụng Caching để Tối ưu hiệu suất) ---
@st.cache_data
@@ -53,7 +51,7 @@ def process_financial_data(df):

return df

# --- Hàm gọi API Gemini ---
# --- Hàm gọi API Gemini cho Phân tích Tài chính (Chức năng 5) ---
def get_ai_analysis(data_for_ai, api_key):
"""Gửi dữ liệu phân tích đến Gemini API và nhận nhận xét."""
try:
@@ -80,13 +78,21 @@ def get_ai_analysis(data_for_ai, api_key):
except Exception as e:
return f"Đã xảy ra lỗi không xác định: {e}"

# --------------------------------------------------------------------------------------
# --- LOGIC CHUNG CỦA ỨNG DỤNG ---
# --------------------------------------------------------------------------------------

# --- Chức năng 1: Tải File ---
uploaded_file = st.file_uploader(
"1. Tải file Excel Báo cáo Tài chính (Chỉ tiêu | Năm trước | Năm sau)",
type=['xlsx', 'xls']
)

# Khởi tạo giá trị mặc định cho chỉ số thanh toán
thanh_toan_hien_hanh_N = "N/A"
thanh_toan_hien_hanh_N_1 = "N/A"
df_processed = None

if uploaded_file is not None:
try:
df_raw = pd.read_excel(uploaded_file)
@@ -113,20 +119,17 @@ def get_ai_analysis(data_for_ai, api_key):
st.subheader("4. Các Chỉ số Tài chính Cơ bản")

try:
                # Lọc giá trị cho Chỉ số Thanh toán Hiện hành (Ví dụ)
                
# Lấy Tài sản ngắn hạn
tsnh_n = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Năm sau'].iloc[0]
tsnh_n_1 = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Năm trước'].iloc[0]

                # Lấy Nợ ngắn hạn (Dùng giá trị giả định hoặc lọc từ file nếu có)
                # **LƯU Ý: Thay thế logic sau nếu bạn có Nợ Ngắn Hạn trong file**
                # Lấy Nợ ngắn hạn
no_ngan_han_N = df_processed[df_processed['Chỉ tiêu'].str.contains('NỢ NGẮN HẠN', case=False, na=False)]['Năm sau'].iloc[0]  
no_ngan_han_N_1 = df_processed[df_processed['Chỉ tiêu'].str.contains('NỢ NGẮN HẠN', case=False, na=False)]['Năm trước'].iloc[0]

                # Tính toán
                thanh_toan_hien_hanh_N = tsnh_n / no_ngan_han_N
                thanh_toan_hien_hanh_N_1 = tsnh_n_1 / no_ngan_han_N_1
                # Tính toán, tránh chia cho 0
                thanh_toan_hien_hanh_N = tsnh_n / no_ngan_han_N if no_ngan_han_N != 0 else 0
                thanh_toan_hien_hanh_N_1 = tsnh_n_1 / no_ngan_han_N_1 if no_ngan_han_N_1 != 0 else 0

col1, col2 = st.columns(2)
with col1:
@@ -142,14 +145,18 @@ def get_ai_analysis(data_for_ai, api_key):
)

except IndexError:
                 st.warning("Thiếu chỉ tiêu 'TÀI SẢN NGẮN HẠN' hoặc 'NỢ NGẮN HẠN' để tính chỉ số.")
                 thanh_toan_hien_hanh_N = "N/A" # Dùng để tránh lỗi ở Chức năng 5
                 thanh_toan_hien_hanh_N_1 = "N/A"
                st.warning("Thiếu chỉ tiêu 'TÀI SẢN NGẮN HẠN' hoặc 'NỢ NGẮN HẠN' để tính chỉ số.")
                thanh_toan_hien_hanh_N = "N/A" 
                thanh_toan_hien_hanh_N_1 = "N/A"

# --- Chức năng 5: Nhận xét AI ---
st.subheader("5. Nhận xét Tình hình Tài chính (AI)")

# Chuẩn bị dữ liệu để gửi cho AI
            # Cần đảm bảo thanh_toan_hien_hanh_N không phải "N/A" khi gửi
            tt_N = f"{thanh_toan_hien_hanh_N:.2f}" if isinstance(thanh_toan_hien_hanh_N, float) else thanh_toan_hien_hanh_N
            tt_N_1 = f"{thanh_toan_hien_hanh_N_1:.2f}" if isinstance(thanh_toan_hien_hanh_N_1, float) else thanh_toan_hien_hanh_N_1
            
data_for_ai = pd.DataFrame({
'Chỉ tiêu': [
'Toàn bộ Bảng phân tích (dữ liệu thô)', 
@@ -160,8 +167,8 @@ def get_ai_analysis(data_for_ai, api_key):
'Giá trị': [
df_processed.to_markdown(index=False),
f"{df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Tốc độ tăng trưởng (%)'].iloc[0]:.2f}%", 
                    f"{thanh_toan_hien_hanh_N_1}", 
                    f"{thanh_toan_hien_hanh_N}"
                    tt_N_1, 
                    tt_N
]
}).to_markdown(index=False) 

@@ -174,7 +181,7 @@ def get_ai_analysis(data_for_ai, api_key):
st.markdown("**Kết quả Phân tích từ Gemini AI:**")
st.info(ai_result)
else:
                     st.error("Lỗi: Không tìm thấy Khóa API. Vui lòng cấu hình Khóa 'GEMINI_API_KEY' trong Streamlit Secrets.")
                    st.error("Lỗi: Không tìm thấy Khóa API. Vui lòng cấu hình Khóa 'GEMINI_API_KEY' trong Streamlit Secrets.")

except ValueError as ve:
st.error(f"Lỗi cấu trúc dữ liệu: {ve}")
@@ -183,3 +190,92 @@ def get_ai_analysis(data_for_ai, api_key):

else:
st.info("Vui lòng tải lên file Excel để bắt đầu phân tích.")

# --------------------------------------------------------------------------------------
# --- CHỨC NĂNG BỔ SUNG: KHUNG CHAT GEMINI ---
# --------------------------------------------------------------------------------------

st.divider()
st.header("💬 Trò chuyện với Gemini (Hỏi Đáp Chung)")

# Lấy API Key từ Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
MODEL_NAME_CHAT = 'gemini-2.5-flash'

# 1. Khởi tạo Client và Session
try:
    if not api_key:
        st.warning("⚠️ Vui lòng cấu hình Khóa 'GEMINI_API_KEY' trong Streamlit Secrets để sử dụng tính năng chat.")
        client = None
    else:
        client = genai.Client(api_key=api_key)

except Exception as e:
    st.error(f"Lỗi khi khởi tạo Gemini Client cho Chat: {e}")
    client = None

# Hàm khởi tạo hoặc lấy đối tượng chat
def get_chat_session(client):
    """Khởi tạo hoặc trả về đối tượng Chat Session từ Gemini."""
    if client and "chat_session" not in st.session_state:
        # Khởi tạo một đối tượng chat mới
        st.session_state.chat_session = client.chats.create(
            model=MODEL_NAME_CHAT,
            system_instruction="Bạn là một trợ lý ảo thân thiện và hữu ích, chuyên giải đáp mọi thắc mắc của người dùng. Hãy trả lời bằng tiếng Việt."
        )
        st.session_state.messages = [] # Lưu trữ lịch sử tin nhắn
    
    # Trả về session nếu client hợp lệ, nếu không trả về None
    return st.session_state.chat_session if client else None

chat = get_chat_session(client)

if chat:
    # 2. Hiển thị lịch sử tin nhắn
    for message in st.session_state.messages:
        role = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(message["content"])

    # 3. Ô NHẬP LIỆU (Chat Input)
    if prompt := st.chat_input("Bạn muốn hỏi Gemini điều gì?"):
        # Hiển thị tin nhắn của người dùng
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Lưu tin nhắn của người dùng vào lịch sử
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gửi tin nhắn đến Gemini và hiển thị phản hồi
        with st.chat_message("assistant"):
            # Sử dụng st.spinner để hiển thị trạng thái tải
            with st.spinner("Đang gửi đến Gemini..."):
                try:
                    # Gửi tin nhắn (prompt) tới phiên chat với streaming
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
                    
                    # 4. Lưu phản hồi vào lịch sử
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

                except Exception as e:
                    error_message = f"Đã xảy ra lỗi khi giao tiếp với Gemini: {e}"
                    st.error(error_message)
                    # Xóa tin nhắn cuối cùng của người dùng nếu có lỗi
                    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                        st.session_state.messages.pop()
else:
    # Chỉ hiện thị thông báo nếu client không được khởi tạo
    pass
