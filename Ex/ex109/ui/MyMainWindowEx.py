import sys
from pathlib import Path

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QGuiApplication, QIcon, QPixmap
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem, QHeaderView

from Ex.ex109.libs.depreciation import (
    parse_amount, parse_years, format_number, calc_original_price,
    calc_annual_depreciation, calc_monthly_depreciation, build_schedule,
)
from Ex.ex109.ui.MyMainWindow import Ui_MainWindow

# Icon gắn cho các QLabel (tên widget -> file trong thư mục images)
LABEL_ICONS = {
    "label_logo": "ic_logo.png", "label_header_art": "ic_header_art.png",
    "label_footer_art": "ic_footer_art.png",
    "label_icon_name": "ic_document.png", "label_icon_purchase": "ic_coins.png",
    "label_icon_transport": "ic_truck.png", "label_icon_install": "ic_wrench.png",
    "label_icon_years": "ic_calendar.png",
    "label_icon_result": "ic_check.png", "label_icon_tip": "ic_info.png",
    "label_icon_res_original": "ic_money.png", "label_icon_res_annual": "ic_chart_green.png",
    "label_icon_res_monthly": "ic_calendar_green.png",
    "label_icon_info_title": "ic_chart_blue_fill.png", "label_icon_table_title": "ic_pie.png",
    "label_icon_stat_original": "ic_coins.png", "label_icon_stat_annual": "ic_calendar_green.png",
    "label_icon_stat_monthly": "ic_calendar_orange.png", "label_icon_stat_years": "ic_calendar_purple.png",
    "label_icon_note": "ic_check.png",
}
# Icon gắn cho các nút
BUTTON_ICONS = {
    "pushButton_calculate": "ic_calc_white.png", "pushButton_detail": "ic_eye_white.png",
    "pushButton_clear": "ic_refresh.png", "pushButton_exit": "ic_exit.png",
}
VND = ' <span style="font-size:8pt">VND</span>'  # đơn vị nhỏ cạnh số


class HidePlaceholderOnFocus(QObject):
    """Chữ gợi ý mờ trong ô nhập: biến mất khi trỏ vào ô, hiện lại nếu rời đi mà ô còn trống."""

    def __init__(self, edits):
        super().__init__(edits[0])
        self.hints = {e: e.placeholderText() for e in edits}
        for e in edits:
            e.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusIn:
            obj.setPlaceholderText("")
        elif event.type() == QEvent.Type.FocusOut:
            obj.setPlaceholderText(self.hints[obj])
        return False


class DepreciationLogic:
    """Toàn bộ xử lý của màn hình khấu hao (viết ở Bài 109).

    Lớp này chỉ giả định giao diện có các widget theo tên chuẩn, nên Bài 130 dùng
    lại bằng cách ghép với Ui_MainWindow của riêng mình.
    """

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)  # Ui_MainWindow đứng sau trong MRO
        self.MainWindow = MainWindow
        self.original_price = self.years = self.monthly = None
        self.detail_widgets = (self.label_icon_table_title, self.label_table_title,
                               self.tableWidget_detail, self.frame_note)
        self.inputs = (self.lineEdit_name, self.lineEdit_purchase,
                       self.lineEdit_transport, self.lineEdit_install, self.lineEdit_years)
        self.load_images()
        self.placeholder_filter = HidePlaceholderOnFocus(list(self.inputs))
        self.setup_table()
        self.set_detail_visible(False)
        self.fit_to_screen()
        self.setupSignalAndSlot()
        # Không để ô đầu tiên tự nhận focus (nếu không chữ mờ sẽ biến mất ngay khi mở)
        self.centralwidget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.centralwidget.setFocus()

    def show_window(self):
        self.MainWindow.show()

    # ---------- giao diện ----------
    def load_images(self):
        """Nạp icon từ thư mục images nằm cạnh thư mục ui (không phụ thuộc thư mục chạy)."""
        images = Path(sys.modules[type(self).__module__].__file__).resolve().parents[1] / "images"
        for name, file in LABEL_ICONS.items():
            getattr(self, name).setPixmap(QPixmap(str(images / file)))
        for name, file in BUTTON_ICONS.items():
            getattr(self, name).setIcon(QIcon(str(images / file)))
        self.pushButton_calculate.setIconSize(self.pushButton_calculate.iconSize() * 1.4)
        self.pushButton_detail.setIconSize(self.pushButton_detail.iconSize() * 1.6)

    def setup_table(self):
        table = self.tableWidget_detail
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setMinimumHeight(52)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(36)

    def fit_to_screen(self):
        """Cỡ cửa sổ vừa màn hình (màn nhỏ/DPI cao thì nội dung tự có thanh cuộn)."""
        area = QGuiApplication.primaryScreen().availableGeometry()
        w, h = min(1280, area.width() - 40), min(860, area.height() - 60)
        self.MainWindow.resize(w, h)
        self.MainWindow.move(area.x() + (area.width() - w) // 2, area.y() + (area.height() - h) // 2)

    def set_detail_visible(self, visible):
        """Bảng chi tiết chỉ hiện sau khi bấm nút 2; ngược lại hiện khung gợi ý."""
        for w in self.detail_widgets:
            w.setVisible(visible)
        self.frame_empty.setVisible(not visible)

    def setupSignalAndSlot(self):
        self.pushButton_calculate.clicked.connect(self.process_calculate)
        self.pushButton_detail.clicked.connect(self.process_detail)
        self.pushButton_clear.clicked.connect(self.process_clear)
        self.pushButton_exit.clicked.connect(self.call_close_app)

    # ---------- xử lý chính ----------
    def process_calculate(self):
        """Nút 1: tính và hiện kết quả ở thẻ bên trái VÀ 4 ô "Thông tin khấu hao" bên phải."""
        try:
            purchase = parse_amount(self.lineEdit_purchase.text(), "giá mua")
            if purchase == 0:
                raise ValueError("Giá mua phải lớn hơn 0!")
            transport = parse_amount(self.lineEdit_transport.text(), "chi phí vận chuyển", required=False)
            install = parse_amount(self.lineEdit_install.text(), "chi phí lắp đặt", required=False)
            years = parse_years(self.lineEdit_years.text())
        except ValueError as err:
            self._show_warning(str(err))
            return False

        original = calc_original_price(purchase, transport, install)
        annual = calc_annual_depreciation(original, years)
        monthly = calc_monthly_depreciation(annual)
        self.original_price, self.years, self.monthly = original, years, monthly

        # thẻ kết quả bên trái
        self.label_val_original.setText(format_number(original))
        self.label_val_annual.setText(format_number(annual))
        self.label_val_monthly.setText(format_number(monthly))
        # vùng thông tin khấu hao bên phải
        self.label_stat_original.setText(format_number(original) + VND)
        self.label_stat_annual.setText(format_number(annual) + VND)
        self.label_stat_monthly.setText(format_number(monthly) + VND)
        self.label_stat_years.setText(f"{years} năm")
        self.set_detail_visible(False)  # dữ liệu mới -> bảng cũ không còn đúng
        return True

    def process_detail(self):
        """Nút 2: hiển thị bảng chi tiết khấu hao từng năm."""
        if not self.process_calculate():  # luôn tính lại theo dữ liệu mới nhất
            return
        schedule = build_schedule(self.original_price, self.years)
        table = self.tableWidget_detail
        table.setRowCount(len(schedule))
        for row, rec in enumerate(schedule):
            cells = [str(rec.year)] + [format_number(v) for v in rec[1:]]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                align = Qt.AlignmentFlag.AlignCenter if col == 0 else \
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                item.setTextAlignment(align)
                table.setItem(row, col, item)

        name = self.lineEdit_name.text().strip() or "Tài sản"
        self.label_note.setText(
            f"<b>{name}:</b> khấu hao hết sau {self.years} năm, giá trị còn lại năm cuối = 0 VND.")
        self.set_detail_visible(True)

    def process_clear(self):
        for edit in self.inputs:
            edit.clear()
        for lbl in (self.label_val_original, self.label_val_annual, self.label_val_monthly,
                    self.label_stat_original, self.label_stat_annual, self.label_stat_monthly,
                    self.label_stat_years):
            lbl.setText("0")
        self.tableWidget_detail.setRowCount(0)
        self.set_detail_visible(False)
        self.original_price = self.years = self.monthly = None
        self.centralwidget.setFocus()  # bỏ focus khỏi ô nhập để chữ mờ hiện lại

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
        msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msgBox.exec() == QMessageBox.StandardButton.Yes:
            exit(0)


class MyMainWindowEx(DepreciationLogic, Ui_MainWindow):
    pass
