import streamlit as st
import pandas as pd

# Cấu hình trang web của ứng dụng
st.set_page_config(page_title="App Tính Thuế TNCN Hàng Loạt 2026", page_icon="💰", layout="wide")

# --- CHÈN LOGO THEO FILE TRỰC TIẾP ---
st.image("logo.JPG", width=250)

# --- THÔNG TIN THÀNH VIÊN VÀ ĐỀ TÀI ---
st.markdown("### 📝 **TS. VŨ ĐỨC BÌNH**")

st.title("💰 Ứng Dụng Tính Thuế Thu Nhập Cá Nhân Hàng Loạt")
st.write("Phiên bản nâng cấp: Cho phép nhập danh sách nhiều người, tự động tính toán và xuất file dữ liệu.")

st.markdown("---")

# --- HÀM LOGIC TÍNH TOÁN AN TOÀN (GIỮ NGUYÊN BẢN CHẤT CỦA BẠN) ---
def tinh_thue_tncn(gross, bonus, overtime, lunch, other, deps):
    total_income = gross + bonus + overtime + lunch + other
    
    bhxh = gross * 0.08
    bhyt = gross * 0.015
    bhtn = gross * 0.01
    total_insurance = bhxh + bhyt + bhtn
    
    self_reduction = 15500000  
    dependent_reduction = deps * 6200000  
    total_reduction = self_reduction + dependent_reduction
    
    exempt_lunch = min(lunch, 730000)
    exempt_allowance = other 
    total_exempt_income = overtime + exempt_lunch + exempt_allowance
    
    assessable_income = max(0, total_income - total_exempt_income - total_insurance - total_reduction)
    
    tax = 0
    brackets = [
        {"limit": 10000000, "rate": 0.05},
        {"limit": 30000000, "rate": 0.10},
        {"limit": 60000000, "rate": 0.20},
        {"limit": 100000000, "rate": 0.30},
        {"limit": float('inf'), "rate": 0.35}
    ]
    
    temp_income = assessable_income
    previous_limit = 0
    for b in brackets:
        range_size = b["limit"] - previous_limit
        if temp_income > 0:
            taxable_in_bracket = min(temp_income, range_size)
            tax += taxable_in_bracket * b["rate"]
            temp_income -= taxable_in_bracket
            previous_limit = b["limit"]
        else:
            break

    net_salary = total_income - total_insurance - tax
    
    return {
        "total_income": total_income,
        "total_insurance": total_insurance,
        "dependent_reduction": dependent_reduction,
        "exempt_lunch": exempt_lunch,
        "exempt_allowance": exempt_allowance,
        "assessable_income": assessable_income,
        "tax": tax,
        "net_salary": net_salary
    }

# --- PHẦN NHẬP DỮ LIỆU ĐẦU VÀO HÀNG LOẠT ---
st.subheader("📋 Bảng nhập thông tin thu nhập danh sách nhân viên")
st.caption("💡 Mẹo: Bạn có thể nhấn nút **'+ Add row'** ở dưới cùng bảng để thêm người mới hoặc click đúp vào ô để sửa số liệu.")

# Khởi tạo dữ liệu mẫu ban đầu
default_data = [
    {
        "Họ và tên": "Nguyễn Văn A",
        "Lương đóng BHXH (VND)": 30000000,
        "Tiền thưởng / Bonus (VND)": 5000000,
        "Lương tăng ca (VND)": 2000000,
        "Phụ cấp ăn trưa (VND)": 800000,
        "Phụ cấp khác (VND)": 1000000,
        "Số người phụ thuộc": 1
    },
    {
        "Họ và tên": "Trần Thị B",
        "Lương đóng BHXH (VND)": 15000000,
        "Tiền thưởng / Bonus (VND)": 0,
        "Lương tăng ca (VND)": 0,
        "Phụ cấp ăn trưa (VND)": 730000,
        "Phụ cấp khác (VND)": 500000,
        "Số người phụ thuộc": 0
    }
]

df_default = pd.DataFrame(default_data)

# Bảng chỉnh sửa dữ liệu động
edited_df = st.data_editor(
    df_default,
    num_rows="dynamic", # Cho phép thêm/xóa dòng tự do
    use_container_width=True,
    column_config={
        "Số người phụ thuộc": st.column_config.NumberColumn(min_value=0, step=1, default=0),
        "Lương đóng BHXH (VND)": st.column_config.NumberColumn(min_value=0, step=500000, default=0),
        "Tiền thưởng / Bonus (VND)": st.column_config.NumberColumn(min_value=0, step=500000, default=0),
        "Lương tăng ca (VND)": st.column_config.NumberColumn(min_value=0, step=500000, default=0),
        "Phụ cấp ăn trưa (VND)": st.column_config.NumberColumn(min_value=0, step=50000, default=0),
        "Phụ cấp khác (VND)": st.column_config.NumberColumn(min_value=0, step=50000, default=0),
    }
)

st.markdown("---")

# --- PHẦN XỬ LÝ VÀ HIỂN THỊ KẾT QUẢ ---
if st.button("🧮 Tính Thuế Cả Danh Sách", type="primary"):
    
    results = []
    
    # Duyệt qua từng dòng người dùng nhập trong bảng
    for index, row in edited_df.iterrows():
        name = row["Họ và tên"] if pd.notna(row["Họ và tên"]) else f"Nhân viên {index + 1}"
        gross = float(row["Lương đóng BHXH (VND)"]) if pd.notna(row["Lương đóng BHXH (VND)"]) else 0.0
        bonus = float(row["Tiền thưởng / Bonus (VND)"]) if pd.notna(row["Tiền thưởng / Bonus (VND)"]) else 0.0
        overtime = float(row["Lương tăng ca (VND)"]) if pd.notna(row["Lương tăng ca (VND)"]) else 0.0
        lunch = float(row["Phụ cấp ăn trưa (VND)"]) if pd.notna(row["Phụ cấp ăn trưa (VND)"]) else 0.0
        other = float(row["Phụ cấp khác (VND)"]) if pd.notna(row["Phụ cấp khác (VND)"]) else 0.0
        deps = int(row["Số người phụ thuộc"]) if pd.notna(row["Số người phụ thuộc"]) else 0
        
        # Gọi hàm tính toán
        res = tinh_thue_tncn(gross, bonus, overtime, lunch, other, deps)
        
        # Lưu kết quả xử lý
        results.append({
            "Họ và tên": name,
            "Tổng thu nhập": res["total_income"],
            "Tổng BH bắt buộc (10.5%)": res["total_insurance"],
            "Miễn thuế (Tăng ca + Ăn trưa trần)": overtime + res["exempt_lunch"] + res["exempt_allowance"],
            "Tổng giảm trừ gia cảnh": 15500000 + res["dependent_reduction"],
            "Thu nhập tính thuế": res["assessable_income"],
            "Thu Thuế TNCN nộp": res["tax"],
            "THỰC NHẬN (NET)": res["net_salary"]
        })
        
    df_results = pd.DataFrame(results)
    
    # 1. Hiển thị thông số tổng quan của cả danh sách
    st.subheader("🎯 Tóm Tắt Toàn Bộ Danh Sách")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Tổng quỹ lương phát sinh", value=f"{df_results['Tổng thu nhập'].sum():,.0f} VND")
    with col2:
        st.metric(label="Tổng tiền thuế TNCN thu về", value=f"{df_results['Thu Thuế TNCN nộp'].sum():,.0f} VND")
    with col3:
        st.metric(label="Tổng thực trả nhân viên (NET)", value=f"{df_results['THỰC NHẬN (NET)'].sum():,.0f} VND")
        
    # 2. Hiển thị bảng kết quả chi tiết
    st.markdown("---")
    st.subheader("📊 Bảng Kết Quả Chi Tiết")
    
    # Định dạng tiền tệ hiển thị cho đẹp
    formatted_df = df_results.style.format({
        "Tổng thu nhập": "{:,.0f} VND",
        "Tổng BH bắt buộc (10.5%)": "{:,.0f} VND",
        "Miễn thuế (Tăng ca + Ăn trưa trần)": "{:,.0f} VND",
        "Tổng giảm trừ gia cảnh": "{:,.0f} VND",
        "Thu nhập tính thuế": "{:,.0f} VND",
        "Thu Thuế TNCN nộp": "{:,.0f} VND",
        "THỰC NHẬN (NET)": "{:,.0f} VND"
    })
    
    st.dataframe(formatted_df, use_container_width=True)
    
    # 3. Tính năng xuất file Excel/CSV cho người dùng tải về
    csv = df_results.to_csv(index=False).encode('utf-8-sig') # Dùng utf-8-sig để không bị lỗi font tiếng Việt khi mở bằng Excel
    st.download_button(
        label="📥 Tải Bảng Kết Quả Về Máy (File .CSV)",
        data=csv,
        file_name="Ket_Qua_Thue_TNCN_2026.csv",
        mime="text/csv",
    )
