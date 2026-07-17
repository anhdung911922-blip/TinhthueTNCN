import streamlit as st
import pandas as pd

# Cấu hình trang web của ứng dụng
st.set_page_config(page_title="App Tính Thuế TNCN Hàng Loạt 2026", page_icon="💰", layout="wide")

# --- CHÈN LOGO THEO FILE TRỰC TIẾP ---
st.image("logo.JPG",width=250)

# --- THÔNG TIN THÀNH VIÊN VÀ ĐỀ TÀI ---
st.markdown("### 📝 **TS. VŨ ĐỨC BÌNH**")

st.title("💰 Ứng Dụng Tính Thuế Thu Nhập Cá Nhân Hàng Loạt")
st.write("Phiên bản nâng cấp: Tự động tạo bảng theo số lượng người tùy chỉnh, tính toán lũy tiến và xuất dữ liệu.")

st.markdown("---")

# --- HÀM LOGIC TÍNH TOÁN AN TOÀN ---
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

# --- PHẦN ĐIỀU CHỈNH SỐ LƯỢNG NGƯỜI ---
st.subheader("⚙️ Cấu hình danh sách")
num_people = st.number_input(
    "Nhập số lượng nhân viên cần tính thuế trong tháng này:", 
    min_value=1, 
    max_value=200, 
    value=3, 
    step=1
)

st.markdown("---")

# --- TỰ ĐỘNG TẠO KHUNG DỮ LIỆU THEO SỐ LƯỢNG ĐÃ CHỌN ---
st.subheader("📋 Bảng nhập thông tin thu nhập chi tiết")
st.caption("💡 Mẹo: Bạn chỉ cần click đúp vào các ô số để sửa nhanh số liệu theo từng người.")

# Khởi tạo danh sách dòng dựa trên số lượng người được chọn
init_data = []
for i in range(int(num_people)):
    init_data.append({
        "Họ và tên": f"Nhân viên {i + 1}",
        "Lương đóng BHXH (VND)": 20000000, # Đặt một số tiền mẫu ban đầu
        "Tiền thưởng / Bonus (VND)": 0,
        "Lương tăng ca (VND)": 0,
        "Phụ cấp ăn trưa (VND)": 730000,   # Tự động điền mức trần miễn thuế mặc định cho tiện
        "Phụ cấp khác (VND)": 0,
        "Số người phụ thuộc": 0
    })

df_default = pd.DataFrame(init_data)

# Bảng chỉnh sửa dữ liệu đồng bộ theo số lượng dòng
edited_df = st.data_editor(
    df_default,
    num_rows="fixed", # Cố định số dòng theo đúng ô nhập số lượng ở trên
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
    
    # Duyệt qua từng dòng dữ liệu trong bảng đã nhập
    for index, row in edited_df.iterrows():
        name = row["Họ và tên"] if pd.notna(row["Họ và tên"]) else f"Nhân viên {index + 1}"
        gross = float(row["Lương đóng BHXH (VND)"]) if pd.notna(row["Lương đóng BHXH (VND)"]) else 0.0
        bonus = float(row["Tiền thưởng / Bonus (VND)"]) if pd.notna(row["Tiền thưởng / Bonus (VND)"]) else 0.0
        overtime = float(row["Lương tăng ca (VND)"]) if pd.notna(row["Lương tăng ca (VND)"]) else 0.0
        lunch = float(row["Phụ cấp ăn trưa (VND)"]) if pd.notna(row["Phụ cấp ăn trưa (VND)"]) else 0.0
        other = float(row["Phụ cấp khác (VND)"]) if pd.notna(row["Phụ cấp khác (VND)"]) else 0.0
        deps = int(row["Số người phụ thuộc"]) if pd.notna(row["Số người phụ thuộc"]) else 0
        
        # Gọi hàm xử lý tính toán từng cá nhân
        res = tinh_thue_tncn(gross, bonus, overtime, lunch, other, deps)
        
        # Lưu lại kết quả sau tính toán
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
    
    # 1. Khối chỉ số tổng quan (Metrics)
    st.subheader("🎯 Tóm Tắt Toàn Bộ Danh Sách")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Tổng quỹ lương phát sinh", value=f"{df_results['Tổng thu nhập'].sum():,.0f} VND")
    with col2:
        st.metric(label="Tổng tiền thuế TNCN thu về", value=f"{df_results['Thu Thuế TNCN nộp'].sum():,.0f} VND")
    with col3:
        st.metric(label="Tổng thực trả nhân viên (NET)", value=f"{df_results['THỰC NHẬN (NET)'].sum():,.0f} VND")
        
    # 2. Bảng kết quả tổng hợp chi tiết từng dòng
    st.markdown("---")
    st.subheader("📊 Bảng Kết Quả Chi Tiết")
    
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
    
    # 3. Nút tải file báo cáo nhanh dạng .CSV mở được trực tiếp bằng Excel
    csv = df_results.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải Bảng Kết Quả Về Máy (File .CSV)",
        data=csv,
        file_name="Ket_Qua_Thue_TNCN_2026.csv",
        mime="text/csv",
    )
