import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from strategy import gen_position

# Nạp hàm khởi tạo client và tải dữ liệu từ thư viện QuantVN
from quantvn.vn.data.utils import client
from quantvn.vn.data import get_stock_hist

def main():
    try:
        # 1. Tải biến môi trường từ file .env (để bảo mật API key)
        load_dotenv()
        
        api_key = os.getenv("QUANTVN_API_KEY")
        if not api_key:
            raise ValueError("Không tìm thấy API Key. Kiểm tra lại file .env")
            
        # 2. Khởi tạo phiên làm việc với máy chủ dữ liệu
        client(apikey=api_key)
        
        # 3. Kéo dữ liệu OHLCV của mã 'VIC' với khung thời gian 1 ngày (1D)
        print("Đang tải dữ liệu mã VIC...")
        df = get_stock_hist("VIC", resolution="1D")
        
        if df is None or df.empty:
            raise ValueError("Dữ liệu tải về bị trống hoặc lỗi kết nối.")
            
        print("Tải dữ liệu thành công. Đang tính toán tín hiệu giao dịch...")
        
        # 4. Áp dụng chiến lược RSI để tạo cột vị thế (position)
        df = gen_position(df)
        
        # 5. Tính tỷ suất sinh lợi hàng ngày của tài sản gốc
        df['returns'] = df['Close'].pct_change()
        
        # 6. Tính lợi nhuận của chiến lược
        # shift(1) để dời vị thế xuống 1 phiên. 
        # tức là vị thế báo cuối ngày hôm nay sẽ được dùng để nhân với lợi nhuận của ngày mai.
        df['strategy_returns'] = df['position'].shift(1) * df['returns']
        
        print("\nĐang tổng hợp các chỉ số hiệu suất...")
        
        # 7. Tính tổng lợi nhuận tích lũy
        cum_bh_return = (1 + df['returns'].fillna(0)).cumprod().iloc[-1] - 1
        cum_strategy_return = (1 + df['strategy_returns'].fillna(0)).cumprod().iloc[-1] - 1
        
        # 8. Đếm tổng số lệnh đã thực hiện
        # Lệnh được ghi nhận khi vị thế thay đổi (khác 0) so với phiên trước
        position_changes = df['position'].diff()
        trades_made = df[(position_changes != 0) & (df['position'] != 0)]
        total_trades = len(trades_made)
        
        # 9. In báo cáo kết quả Backtest
        print("="*40)
        print("KẾT QUẢ BACKTEST (MÃ VIC) - CHIẾN LƯỢC RSI")
        print("="*40)
        print(f"Lợi nhuận Mua & Nắm giữ (Buy & Hold): {cum_bh_return * 100:.2f}%")
        print(f"Lợi nhuận Chiến lược (Strategy):      {cum_strategy_return * 100:.2f}%")
        print(f"Tổng số lệnh đã khớp:                 {total_trades}")
        print("="*40)
        
        # 10. Kiểm tra chéo: Xem 10 phiên gần nhất có phát sinh vị thế
        print("\nKiểm tra chéo: 10 phiên gần nhất có vị thế giao dịch (position != 0)")
        positions_only = df[df['position'] != 0].copy()
        if not positions_only.empty:
            print(positions_only[['Close', 'RSI', 'position', 'returns', 'strategy_returns']].tail(10))
        else:
            print("Không có vị thế nào được tạo ra trong giai đoạn này.")
            
    except Exception as e:
        print(f"Có lỗi xảy ra trong quá trình backtest: {e}")

if __name__ == "__main__":
    main()