"""Bài 130 dùng lại toàn bộ logic đã viết ở Bài 109 (không viết lại)."""
from Ex.ex109.libs.depreciation import (  # noqa: F401
    DepreciationRow,
    parse_amount,
    parse_years,
    format_number,
    calc_original_price,
    calc_annual_depreciation,
    calc_monthly_depreciation,
    build_schedule,
)
