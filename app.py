import streamlit as st

# Cấu hình trang web của ứng dụng
st.set_page_config(page_title="App Tính Thuế TNCN Việt Nam 2026", page_icon="💰", layout="centered")

# --- CHÈN LOGO THEO FILE TRỰC TIẾP ---
st.image("logo.jpg")

# --- THÔNG TIN THÀNH VIÊN VÀ ĐỀ TÀI ---
st.markdown("### 📝 **TS. VŨ ĐỨC BÌNH**")

st.title("💰 Ứng Dụng Tính Thuế Thu Nhập Cá Nhân")
st.write("Cập nhật đầy đủ Lương, Thưởng, Tăng ca, Phụ cấp theo luật thuế mới nhất năm 2026")

st.markdown("---")

# --- PHẦN NHẬP DỮ LIỆU ĐẦU VÀO ---
st.subheader("📋 Nhập thông tin thu nhập tháng này của bạn")

gross_salary = st.number_input(
    "1. Lương đóng BHXH (VND):", 
    min_value=0, value=30000000, step=500000, format="%d"
)

gross_bonus_pay = st.number_input(
    "2. Tiền thưởng / Bonus (VND):", 
    min_value=0, value=0, step=500000, format="%d"
)

overtime_pay = st.number_input(
    "3. Tiền lương tăng ca / làm thêm giờ (VND):", 
    min_value=0, value=0, step=500000, format="%d"
)

st.markdown("**4. Các khoản phụ cấp nhận bằng tiền mặt:**")
col_sub1, col_sub2 = st.columns(2)
with col_sub1:
    # Đã bỏ ghi chú tối đa
    lunch_allowance = st.number_input("Phụ cấp ăn trưa (VND):", min_value=0, value=0, step=50000)
with col_sub2:
    other_allowance = st.number_input("Phụ cấp điện thoại, xăng xe (VND):", min_value=0, value=0, step=50000)

dependents = st.number_input(
    "5. Số người phụ thuộc bạn đang nuôi dưỡng (người):", 
    min_value=0, value=1, step=1
)

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
        {"limit": 10000000, "rate": 0.05, "desc": "Bậc 1: Đến 10 triệu đồng (5%)"},
        {"limit": 30000000, "rate": 0.10, "desc": "Bậc 2: Trên 10 đến 30 triệu đồng (10%)"},
        {"limit": 60000000, "rate": 0.20, "desc": "Bậc 3: Trên 30 đến 60 triệu đồng (20%)"},
        {"limit": 100000000, "rate": 0.30, "desc": "Bậc 4: Trên 60 đến 100 triệu đồng (30%)"},
        {"limit": float('inf'), "rate": 0.35, "desc": "Bậc 5: Trên 100 triệu đồng (35%)"}
    ]
    
    temp_income = assessable_income
    previous_limit = 0
    tax_breakdown = []
    for b in brackets:
      range_size = b["limit"] - previous_limit
        if temp_income > 0:
            taxable_in_bracket = min(temp_income, range_size)
            tax_in_bracket = taxable_in_bracket * b["rate"]
            tax += tax_in_bracket
            
            tax_breakdown.append({
                "Bậc thuế": b["desc"],
                "Thu nhập tính thuế ở bậc này": f"{taxable_in_bracket:,.0f} VND",
                "Tiền thuế phải nộp": f"{tax_in_bracket:,.0f} VND"
            })
            
            temp_income -= taxable_in_bracket
            previous_limit = b["limit"]
        else:
            break

    net_salary = total_income - total_insurance - tax
    
    return {
        "total_income": total_income, "bhxh": bhxh, "bhyt": bhyt, "bhtn": bhtn,
        "total_insurance": total_insurance, "dependent_reduction": dependent_reduction,
        "exempt_lunch": exempt_lunch, "exempt_allowance": exempt_allowance,
        "assessable_income": assessable_income, "tax": tax, "net_salary": net_salary,
        "tax_breakdown": tax_breakdown
    }

# --- PHẦN NÚT BẤM KÍCH HOẠT VÀ HIỂN THỊ KẾT QUẢ ---
if st.button("🧮 Tính Thuế & Nhận Kết Quả", type="primary"):
    res = tinh_thue_tncn(gross_salary, gross_bonus_pay, overtime_pay, lunch_allowance, other_allowance, dependents)
    
    st.markdown("---")
    st.subheader("🎯 Kết Quả Tính Toán Tóm Tắt")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Tổng thu nhập nhận được (Lương + Thưởng + Phụ cấp)", value=f"{res['total_income']:,.0f} VND")
        st.metric(label="Tổng bảo hiểm bắt buộc trừ vào lương (10.5%)", value=f"{res['total_insurance']:,.0f} VND")
    with col2:
        st.metric(label="Thuế TNCN phải nộp", value=f"{res['tax']:,.0f} VND")
        st.metric(label="THỰC NHẬN VỀ TAY (NET)", value=f"{res['net_salary']:,.0f} VND")

    st.markdown("---")
    st.subheader("📜 Giải Trình Chi Tiết Quy Trình Khấu Trừ (Năm 2026)")
    
    st.markdown(f"""
    * **Tổng thu nhập phát sinh trong tháng:** `{res['total_income']:,.0f} VND`
    * **Các khoản được miễn trừ thuế:**
        * Tiền lương tăng ca: `{overtime_pay:,.0f} VND`
        * Tiền ăn trưa được miễn: `{res['exempt_lunch']:,.0f} VND`
        * Phụ cấp công việc (xăng xe, điện thoại): `{res['exempt_allowance']:,.0f} VND`
    * **Các khoản phí bảo hiểm bắt buộc trích từ lương chính:**
        * BHXH (8%): `{res['bhxh']:,.0f} VND` | BHYT (1.5%): `{res['bhyt']:,.0f} VND` | BHTN (1%): `{res['bhtn']:,.0f} VND`
        * **Tổng phí bảo hiểm:** `{res['total_insurance']:,.0f} VND`
    * **Giảm trừ gia cảnh:**
        * Giảm trừ bản thân người nộp: `15,500,000 VND`
    * Giảm trừ người phụ thuộc: `{res['dependent_reduction']:,.0f} VND` (cho {dependents} người)
  * **Thu nhập tính thuế (đưa vào bảng lũy tiến):** `{res['assessable_income']:,.0f} VND`
    """)
    
    if res['tax'] > 0:
        st.write("📊 **Chi tiết phân tách số tiền nộp theo biểu thuế 5 bậc mới (2026):**")
        st.table(res['tax_breakdown'])
    else:
        st.success("Tuyệt vời! Sau khi trừ các khoản phụ cấp miễn thuế và giảm trừ gia cảnh, thu nhập tính thuế của bạn bằng 0 nên không cần phải nộp thuế TNCN.")
