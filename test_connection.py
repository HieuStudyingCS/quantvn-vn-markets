import os
from dotenv import load_dotenv
from quantvn.vn.data.utils import client
from quantvn.vn.data import get_stock_hist

# 1. Tải các biến môi trường từ file .env lên hệ thống
load_dotenv()

# 2. Lấy API key từ biến môi trường
api_key = os.getenv("QUANTVN_API_KEY")

if not api_key:
    print("Lỗi: Không tìm thấy API Key. Kiểm tra lại cấu trúc file .env trước khi thực thi tiếp")
else:
    try:
        # 3. Khởi tạo client bằng key lấy từ .env 
        client(apikey=api_key)
        
        # 4. Test lấy dữ liệu theo đúng chuẩn bài test
        print("Đang kết nối để lấy dữ liệu mã VIC...")
        df = get_stock_hist("VIC", resolution="1H")
        
        print("Kết nối thành công! Dữ liệu 5 dòng cuối:")
        print(df.tail())
    except Exception as e:
        print(f"Có lỗi xảy ra trong quá trình kết nối: {e}")