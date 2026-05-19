import pandas as pd
import numpy as np

def gen_position(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo tín hiệu giao dịch dựa trên RSI.
    
    Tham số:
    df (pd.DataFrame): Bảng dữ liệu đầu vào, bắt buộc phải có cột 'Close' (Giá đóng cửa).
    
    Kết quả trả về:
    pd.DataFrame: Bảng dữ liệu gốc được bổ sung thêm 2 cột: 'RSI' và 'position' (vị thế).
    """
    # 1. Kiểm tra tính toàn vẹn của dữ liệu: Phải có cột giá đóng cửa
    if 'Close' not in df.columns:
        raise ValueError("Dữ liệu đầu vào bắt buộc phải chứa cột 'Close'")

    # 2. Cài đặt chu kỳ tính RSI (tiêu chuẩn thường dùng là 14 phiên)
    period = 14
    
    # 3. Tính toán mức chênh lệch giá giữa phiên hiện tại và phiên liền trước
    delta = df['Close'].diff()
    
    # 4. Tách biệt các phiên tăng giá (gain) và phiên giảm giá (loss)
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # 5. Tính giá trị trung bình trượt mũ (EMA) cho biên độ tăng và giảm
    # Sử dụng phương pháp làm mượt của Wilder với hệ số alpha = 1 / chu kỳ
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    # 6. Tính Relative Strength
    # Tạm thời bỏ qua cảnh báo chia cho 0 để hệ thống không bị crash khi avg_loss = 0
    with np.errstate(divide='ignore', invalid='ignore'):
        rs = avg_gain / avg_loss
    
    # 7. Tính toán chỉ số RSI hoàn chỉnh
    # Xử lý ngoại lệ: Nếu không có phiên giảm nào (avg_loss = 0), RSI mặc định là mức tối đa 100
    rsi = np.where(avg_loss == 0, 100, 100 - (100 / (1 + rs)))
    df['RSI'] = rsi
    
# 8. Xây dựng logic tạo tín hiệu (vị thế) giao dịch
    df['position'] = 0 # Mặc định ban đầu là 0 (Đứng ngoài)
    
    # Kích hoạt vị thế Mua (1) khi RSI rơi vào vùng quá bán (RSI < 30)
    df.loc[df['RSI'] < 30, 'position'] = 1
    
    # Kích hoạt vị thế Bán (-1) khi RSI rơi vào vùng quá mua (RSI > 70)
    df.loc[df['RSI'] > 70, 'position'] = -1
    
    # 9. Dọn dẹp dữ liệu
    df['position'] = df['position'].fillna(0).astype(int)
    
    return df