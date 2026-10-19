from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt

from Ex.ex130.libs.depreciation import (
    calc_original_price,
    calc_annual_depreciation,
    calc_monthly_depreciation,
    build_schedule,
)
from Ex.ex130.ui.MyMainWindow import Ui_MainWindow


class MyMainWindowEx(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.original_price = None  # lưu kết quả sau khi bấm "Tính Khấu Hao"
        self.years = None
        self.tableWidget_detail.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.tableWidget_detail.verticalHeader().setVisible(False)
        self.setupSignalAndSlot()

    def show_window(self):
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        self.pushButton_calculate.clicked.connect(self.process_calculate)
        self.pushButton_detail.clicked.connect(self.process_detail)
        self.pushButton_clear.clicked.connect(self.process_clear)
        self.pushButton_exit.clicked.connect(self.call_close_app)

    # ---------- xử lý chính ----------
    def _read_money(self, line_edit, field_name, required=True):
        """Đọc số tiền từ ô nhập (cho phép dấu , hoặc khoảng trắng). Trả về None nếu lỗi."""
        text = line_edit.text().strip().replace(",", "").replace(" ", "")
        if text == "":
            if required:
                self._show_warning(f"Vui lòng nhập {field_name}!")
                line_edit.setFocus()
                return None
            return 0.0  # không có chi phí -> mặc định 0
        try:
            value = float(text)
        except ValueError:
            self._show_warning(f"{field_name} phải là số. Vui lòng nhập lại!")
            line_edit.selectAll()
            line_edit.setFocus()
            return None
        if value < 0:
            self._show_warning(f"{field_name} không được âm!")
            line_edit.setFocus()
            return None
        return value

    def process_calculate(self):
        """Nút 1: tính Nguyên giá, Mức khấu hao năm, Mức khấu hao tháng. Trả về True nếu hợp lệ."""
        purchase = self._read_money(self.lineEdit_purchase, "giá mua")
        if purchase is None:
            return False
        if purchase == 0:
            self._show_warning("Giá mua phải lớn hơn 0!")
            self.lineEdit_purchase.setFocus()
            return False
        transport = self._read_money(self.lineEdit_transport, "chi phí vận chuyển", required=False)
        if transport is None:
            return False
        install = self._read_money(self.lineEdit_install, "chi phí lắp đặt", required=False)
        if install is None:
            return False
        years = self.spinBox_years.value()

        original = calc_original_price(purchase, transport, install)
        annual = calc_annual_depreciation(original, years)
        monthly = calc_monthly_depreciation(annual)

        self.original_price = original
        self.years = years
        self.lineEdit_original.setText(f"{original:,.0f} VND")
        self.lineEdit_annual.setText(f"{annual:,.0f} VND")
        self.lineEdit_monthly.setText(f"{monthly:,.0f} VND")
        self.tableWidget_detail.setRowCount(0)
        self.label_summary.setText("")
        return True

    def process_detail(self):
        """Nút 2: hiển thị bảng chi tiết khấu hao từng năm."""
        if not self.process_calculate():  # luôn tính lại theo dữ liệu mới nhất
            return
        schedule = build_schedule(self.original_price, self.years)
        self.tableWidget_detail.setRowCount(len(schedule))
        for row, (year, dep, acc, remain) in enumerate(schedule):
            values = [str(year), f"{dep:,.0f}", f"{acc:,.0f}", f"{remain:,.0f}"]
            for col, text in enumerate(values):
                item = QTableWidgetItem(text)
                align = Qt.AlignmentFlag.AlignCenter if col == 0 else \
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                item.setTextAlignment(align)
                self.tableWidget_detail.setItem(row, col, item)
        name = self.lineEdit_name.text().strip() or "Tài sản"
        self.label_summary.setText(
            f"{name}: khấu hao hết sau {self.years} năm, "
            f"giá trị còn lại năm cuối = 0 VND.")

    def process_clear(self):
        self.lineEdit_name.clear()
        self.lineEdit_purchase.clear()
        self.lineEdit_transport.setText("0")
        self.lineEdit_install.setText("0")
        self.spinBox_years.setValue(5)
        self.lineEdit_original.clear()
        self.lineEdit_annual.clear()
        self.lineEdit_monthly.clear()
        self.tableWidget_detail.setRowCount(0)
        self.label_summary.setText("")
        self.original_price = None
        self.years = None
        self.lineEdit_name.setFocus()

    # ---------- hộp thoại ----------
    def _show_warning(self, message):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Lỗi dữ liệu")
        msgBox.setText(message)
        msgBox.setIcon(QMessageBox.Icon.Warning)
        msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgBox.exec()

    def call_close_app(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Xác nhận thoát")
        msgBox.setText("Bạn muốn thoát hay không?")
        msgBox.setIcon(QMessageBox.Icon.Question)
        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        msgBox.setStandardButtons(buttons)
        ret = msgBox.exec()
        if ret == QMessageBox.StandardButton.Yes:
            exit(0)
