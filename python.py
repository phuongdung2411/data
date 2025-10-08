import streamlit as st
import pandas as pd
from google import genai
from google.genai.errors import APIError

# --- Cấu hình Trang Streamlit ---
st.set_page_config(
    page_title="App Phân Tích Báo Cáo Tài Chính",
    layout="wide"
)

st.title("Ứng dụng Phân Tích Báo Cáo Tài chính 📊")

# --- Hàm tính toán chính (Sử dụng Caching để Tối ưu hiệu suất) ---
@st.cache_data
def process_financial_data(df):
    """Thực hiện các phép tính Tăng trưởng và Tỷ trọng."""
    
    # Đảm bảo các giá trị là số để tính toán
    numeric_cols = ['Năm trước', 'Năm sau']
    for col in numeric_cols:
        # Đảm bảo chuyển đổi Series (df[col]) sang số, và điền 0 cho NaN
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 1. Tính Tốc độ Tăng trưởng
    df['Tốc độ tăng trưởng (%)'] = (
        (df['Năm sau'] - df['Năm trước']) / df['Năm trước'].replace(0, 1e-9)
    ) * 100

    # 2. Tính Tỷ trọng theo Tổng Tài sản
    tong_tai_san_row = df[df['Chỉ tiêu'].str.contains('TỔNG CỘNG TÀI SẢN', case=False, na=False)]
    
    if tong_tai_san_row.empty:
        # Nếu không tìm thấy dòng "TỔNG CỘNG TÀI SẢN"
        if df['Năm trước'].sum() > 0 or df['Năm sau'].sum() > 0:
            # Sử dụng tổng của các cột làm giá trị tổng tài sản (chỉ là giải pháp dự phòng)
            tong_tai_san_N_1 = df['Năm trước'].sum()
            tong_tai_san_N = df['Năm sau'].sum()
        else:
             raise ValueError("Không tìm thấy chỉ tiêu 'TỔNG CỘNG TÀI SẢN' và không có dữ liệu để tổng hợp.")
    else:
        tong_tai_san_N_1 = tong_tai_san_row['Năm trước'].iloc[0]
        tong_tai_san_N = tong_tai_san_row['Năm sau'].iloc[0]

    # Xử lý trường hợp mẫu số bằng 0 thủ công
    divisor_N_1 = tong_tai_san_N_1 if tong_tai_san_N_1 != 0 else 1e-9
    divisor_N = tong_tai_san_N if tong_tai_san_N != 0 else 1e-9

    # Tính tỷ trọng với mẫu số đã được xử lý
    df['Tỷ trọng Năm trước (%)'] = (df['Năm trước'] / divisor_N_1) * 100
    df['Tỷ trọng Năm sau (%)'] = (df['Năm sau'] / divisor_N) * 100
    
    return df

# --- Hàm gọi API Gemini cho Phân tích Tài chính (Chức năng 5) ---
def get_ai_analysis(data_for_ai, api_key):
    """Gửi dữ liệu phân tích đến Gemini API và nhận nhận xét."""
    try:
        client = genai.Client(api_key=api_key)
        model_name = 'gemini-2.5-flash' 

        prompt = f"""
        Bạn là một chuyên gia phân tích tài chính chuyên nghiệp. Dựa trên các chỉ số tài chính sau, hãy đưa ra một nhận xét khách quan, ngắn gọn (khoảng 3-4 đoạn) về tình hình tài chính của doanh nghiệp. Đánh giá tập trung vào tốc độ tăng trưởng, thay đổi cơ cấu tài sản và khả năng thanh toán hiện hành.
        
        Dữ liệu thô và chỉ số:
        {data_for_ai}
        """

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return response.text

    except APIError as e:
        return f"Lỗi gọi Gemini API: Vui lòng kiểm tra Khóa API hoặc giới hạn sử dụng. Chi tiết lỗi: {e}"
    except KeyError:
        return "Lỗi: Không tìm thấy Khóa API 'GEMINI_API_KEY'. Vui lòng kiểm tra cấu hình Secrets trên Streamlit Cloud."
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
        
        # Tiền xử lý: Đảm bảo chỉ có 3 cột quan trọng
        df_raw.columns = ['Chỉ tiêu', 'Năm trước', 'Năm sau']
        
        # Xử lý dữ liệu
        df_processed = process_financial_data(df_raw.copy())

        if df_processed is not None:
            
            # --- Chức năng 2 & 3: Hiển thị Kết quả ---
            st.subheader("2. Tốc độ Tăng trưởng & 3. Tỷ trọng Cơ cấu Tài sản")
            st.dataframe(df_processed.style.format({
                'Năm trước': '{:,.0f}',
                'Năm sau': '{:,.0f}',
                'Tốc độ tăng trưởng (%)': '{:.2f}%',
                'Tỷ trọng Năm trước (%)': '{:.2f}%',
                'Tỷ trọng Năm sau (%)': '{:.2f}%'
            }), use_container_width=True)
            
            # --- Chức năng 4: Tính Chỉ số Tài chính ---
            st.subheader("4. Các Chỉ số Tài chính Cơ bản")
            
            try:
                # Lấy Tài sản ngắn hạn
                tsnh_n = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Năm sau'].iloc[0]
                tsnh_n_1 = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Năm trước'].iloc[0]

                # Lấy Nợ ngắn hạn
                no_ngan_han_N = df_processed[df_processed['Chỉ tiêu'].str.contains('NỢ NGẮN HẠN', case=False, na=False)]['Năm sau'].iloc[0]  
                no_ngan_han_N_1 = df_processed[df_processed['Chỉ tiêu'].str.contains('NỢ NGẮN HẠN', case=False, na=False)]['Năm trước'].iloc[0]

                # Tính toán, tránh chia cho 0
                thanh_toan_hien_hanh_N = tsnh_n / no_ngan_han_N if no_ngan_han_N != 0 else 0
                thanh_toan_hien_hanh_N_1 = tsnh_n_1 / no_ngan_han_N_1 if no_ngan_han_N_1 != 0 else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Chỉ số Thanh toán Hiện hành (Năm trước)",
                        value=f"{thanh_toan_hien_hanh_N_1:.2f} lần"
                    )
                with col2:
                    st.metric(
                        label="Chỉ số Thanh toán Hiện hành (Năm sau)",
                        value=f"{thanh_toan_hien_hanh_N:.2f} lần",
                        delta=f"{thanh_toan_hien_hanh_N - thanh_toan_hien_hanh_N_1:.2f}"
                    )
                    
            except IndexError:
                st.warning("Thiếu chỉ tiêu 'TÀI SẢN NGẮN HẠN' hoặc 'NỢ NGẮN HẠN' để tính chỉ số.")
                thanh_toan_hien_hanh_N = "N/A" 
                thanh_toan_hien_hanh_N_1 = "N/A"
            
            # --- Chức năng 5: Nhận xét AI ---
            st.subheader("5. Nhận xét Tình hình Tài chính (AI)")
            
            # Chuẩn bị dữ liệu để gửi cho AI
            tt_N = f"{thanh_toan_hien_hanh_N:.2f}" if isinstance(thanh_toan_hien_hanh_N, float) else thanh_toan_hien_hanh_N
            tt_N_1 = f"{thanh_toan_hien_hanh_N_1:.2f}" if isinstance(thanh_toan_hien_hanh_N_1, float) else thanh_toan_hien_hanh_N_1
            
            # Lấy tăng trưởng TSNH an toàn hơn
            try:
                tsnh_growth = df_processed[df_processed['Chỉ tiêu'].str.contains('TÀI SẢN NGẮN HẠN', case=False, na=False)]['Tốc độ tăng trưởng (%)'].iloc[0]
                tsnh_growth_str = f"{tsnh_growth:.2f}%"
            except IndexError:
                tsnh_growth_str = "Không xác định"

            data_for_ai = pd.DataFrame({
                'Chỉ tiêu': [
                    'Toàn bộ Bảng phân tích (dữ liệu thô)', 
                    'Tăng trưởng Tài sản ngắn hạn (%)', 
                    'Thanh toán hiện hành (N-1)', 
                    'Thanh toán hiện hành (N)'
                ],
                'Giá trị': [
                    df_processed.to_markdown(index=False),
                    tsnh_growth_str, 
                    tt_N_1, 
                    tt_N
                ]
            }).to_markdown(index=False) 

            if st.button("Yêu cầu AI Phân tích"):
                api_key = st.secrets.get("GEMINI_API_KEY") 
                
                if api_key:
                    with st.spinner('Đang gửi dữ liệu và chờ Gemini phân tích...'):
                        ai_result = get_ai_analysis(data_for_ai, api_key)
                        st.markdown("**Kết quả Phân tích từ Gemini AI:**")
                        st.info(ai_result)
                else:
                    st.error("Lỗi: Không tìm thấy Khóa API. Vui lòng cấu hình Khóa 'GEMINI_API_KEY' trong Streamlit Secrets.")

    except ValueError as ve:
        st.error(f"Lỗi cấu trúc dữ liệu: {ve}")
    except Exception as e:
        st.error(f"Có lỗi xảy ra khi đọc hoặc xử lý file: {e}. Vui lòng kiểm tra định dạng file.")

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
    client = None
    if not api_key:
        st.warning("⚠️ Vui lòng cấu hình Khóa **'GEMINI_API_KEY'** trong Streamlit Secrets để sử dụng tính năng chat.")
    else:
        client = genai.Client(api_key=api_key)

except Exception as e:
    st.error(f"Lỗi khi khởi tạo Gemini Client: {e}")
    client = None

# Hàm khởi tạo hoặc lấy đối tượng chat
def get_chat_session(client):
    """Khởi tạo hoặc trả về đối tượng Chat Session từ Gemini."""
    if client and "chat_session" not in st.session_state:
        try:
            # Khởi tạo một đối tượng chat mới
            st.session_state.chat_session = client.chats.create(
                model=MODEL_NAME_CHAT,
                system_instruction="Bạn là một trợ lý ảo thân thiện và hữu ích, chuyên giải đáp mọi thắc mắc của người dùng. Hãy trả lời bằng tiếng Việt."
            )
            st.session_state.messages = [] # Lưu trữ lịch sử tin nhắn
        except APIError as e:
            # Bắt lỗi API cụ thể (ví dụ: xác thực thất bại)
            st.error(f"Lỗi API khi khởi tạo phiên chat: Vui lòng kiểm tra Khóa API của bạn có hợp lệ không. Chi tiết: {e}")
            return None
        except Exception as e:
            st.error(f"Lỗi không xác định khi khởi tạo phiên chat: {e}")
            return None

    # Trả về session nếu client hợp lệ và session đã được tạo
    return st.session_state.chat_session if client and "chat_session" in st.session_state else None

chat = get_chat_session(client)

if chat:
    # 2. Hiển thị lịch sử tin nhắn
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
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
