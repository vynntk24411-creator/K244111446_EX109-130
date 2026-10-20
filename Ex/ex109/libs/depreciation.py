"""
Tính khấu hao tài sản cố định theo phương pháp đường thẳng.

Module thuần logic (KHÔNG phụ thuộc giao diện) -> Bài 109 viết, Bài 130 dùng lại.
"""
from collections import namedtuple

# Một dòng của bảng khấu hao
DepreciationRow = namedtuple(
    "DepreciationRow", "year opening depreciation accumulated remaining")


def parse_amount(text, field_name, required=True):
    """Đọc số tiền từ chuỗi (chấp nhận dấu , và khoảng trắng).

    - Ô trống: báo lỗi nếu bắt buộc, ngược lại trả về 0 (không có chi phí).
    - Sai định dạng hoặc số âm: ném ValueError kèm thông báo tiếng Việt.
    """
    text = text.strip().replace(",", "").replace(" ", "")
    if not text:
        if required:
            raise ValueError(f"Vui lòng nhập {field_name}!")
        return 0.0
    try:
        value = float(text)
    except ValueError:
        raise ValueError(f"{field_name} phải là số. Vui lòng nhập lại!") from None
    if value < 0:
        raise ValueError(f"{field_name} không được âm!")
    return value


def parse_years(text):
    """Đọc số năm khấu hao (số nguyên >= 1)."""
    text = text.strip()
    if not text:
        raise ValueError("Vui lòng nhập số năm khấu hao!")
    if not text.isdigit() or int(text) < 1:
        raise ValueError("Số năm khấu hao phải là số nguyên lớn hơn 0!")
    return int(text)


def format_number(value):
    """Định dạng số có phân cách hàng nghìn: 127000000 -> '127,000,000'."""
    return f"{value:,.0f}"


def calc_original_price(purchase_price, transport_cost=0, install_cost=0):
    """Nguyên giá = giá mua + chi phí vận chuyển + chi phí lắp đặt, chạy thử."""
    return purchase_price + transport_cost + install_cost


def calc_annual_depreciation(original_price, years):
    """Mức khấu hao hằng năm = Nguyên giá / số năm khấu hao."""
    if years <= 0:
        raise ValueError("Số năm khấu hao phải lớn hơn 0")
    return original_price / years


def calc_monthly_depreciation(annual_depreciation):
    """Mức khấu hao hằng tháng = Mức khấu hao hằng năm / 12."""
    return annual_depreciation / 12


def build_schedule(original_price, years):
    """Tính chi tiết khấu hao từng năm bằng vòng lặp.

    Trả về list DepreciationRow(year, opening, depreciation, accumulated, remaining).
    Năm cuối: khấu hao = Nguyên giá - Hao mòn lũy kế  => giá trị còn lại = 0.
    """
    annual = calc_annual_depreciation(original_price, years)
    schedule, accumulated = [], 0.0
    for year in range(1, years + 1):
        opening = original_price - accumulated
        # Kỳ cuối lấy phần còn lại để không bị lệch do làm tròn
        depreciation = opening if year == years else annual
        accumulated += depreciation
        schedule.append(DepreciationRow(
            year, opening, depreciation, accumulated, original_price - accumulated))
    return schedule
