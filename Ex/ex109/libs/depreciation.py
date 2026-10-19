"""
Module tính khấu hao tài sản cố định theo phương pháp đường thẳng.
Module này KHÔNG phụ thuộc giao diện nên dùng lại được cho bài 109 và bài 130.
"""


def calc_original_price(purchase_price, transport_cost=0, install_cost=0):
    """Nguyên giá = giá mua + chi phí vận chuyển + chi phí lắp đặt, chạy thử..."""
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
    """
    Tính chi tiết khấu hao từng năm bằng vòng lặp.
    Trả về list các tuple: (năm, khấu hao trong năm, hao mòn lũy kế, giá trị còn lại)
    Năm cuối: khấu hao = Nguyên giá - Hao mòn lũy kế => giá trị còn lại = 0.
    """
    if years <= 0:
        raise ValueError("Số năm khấu hao phải lớn hơn 0")
    annual = calc_annual_depreciation(original_price, years)
    schedule = []
    accumulated = 0
    for year in range(1, years + 1):
        if year == years:  # kỳ cuối
            depreciation = original_price - accumulated
            accumulated = original_price
            remaining = 0
        else:
            depreciation = annual
            accumulated += depreciation
            remaining = original_price - accumulated
        schedule.append((year, depreciation, accumulated, remaining))
    return schedule
