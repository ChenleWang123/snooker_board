import sys
from copy import deepcopy
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QInputDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import QEvent, QPointF, QPropertyAnimation, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QKeyEvent, QPainter, QPen, QPolygonF, QRadialGradient


class BallDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.counts = {
            "red": 15,
            "yellow": 1,
            "green": 1,
            "brown": 1,
            "blue": 1,
            "pink": 1,
            "black": 1,
        }
        self.ball_colors = {
            "red": QColor("#ef3f5d"),
            "yellow": QColor("#facc15"),
            "green": QColor("#35d976"),
            "brown": QColor("#8b5e57"),
            "blue": QColor("#3b82f6"),
            "pink": QColor("#ff69b4"),
            "black": QColor("#3f3a4d"),
        }
        self.setMinimumHeight(88)

    def set_counts(self, reds, colors):
        self.counts = {
            "red": reds,
            "yellow": colors["yellow"],
            "green": colors["green"],
            "brown": colors["brown"],
            "blue": colors["blue"],
            "pink": colors["pink"],
            "black": colors["black"],
        }
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#050505"))

        names = ["red", "yellow", "green", "brown", "blue", "pink", "black"]
        radius = 20
        gap = 36
        number_gap = 16
        font = QFont("Arial", 30)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        number_widths = [metrics.horizontalAdvance(str(self.counts[name])) for name in names]
        item_widths = [(radius * 2) + number_gap + width for width in number_widths]
        total_width = sum(item_widths) + gap * (len(names) - 1)
        x = max(20, (self.width() - total_width) / 2)
        center_y = self.height() / 2 - 8

        for index, name in enumerate(names):
            self.draw_ball(painter, x + radius, center_y, radius, self.ball_colors[name])
            painter.setPen(Qt.GlobalColor.white)
            text_x = x + radius * 2 + number_gap
            text_rect = QRectF(text_x, center_y - 32, number_widths[index] + 8, 64)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, str(self.counts[name]))
            x += item_widths[index] + gap

    def draw_ball(self, painter, cx, cy, radius, color):
        ball = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        gradient = QRadialGradient(cx - radius * 0.35, cy - radius * 0.45, radius * 1.35)
        gradient.setColorAt(0.0, color.lighter(175))
        gradient.setColorAt(0.42, color)
        gradient.setColorAt(1.0, color.darker(170))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(ball)

        shine = QRadialGradient(cx - radius * 0.38, cy - radius * 0.48, radius * 0.58)
        shine.setColorAt(0.0, QColor(255, 255, 255, 190))
        shine.setColorAt(0.55, QColor(255, 255, 255, 50))
        shine.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(shine)
        painter.drawEllipse(QRectF(cx - radius * 0.78, cy - radius * 0.86, radius * 0.9, radius * 0.68))


class PotHistoryDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.values = []
        self.background = QColor("#0b1020")
        self.ball_colors = {
            1: QColor("#ef3f5d"),
            2: QColor("#facc15"),
            3: QColor("#35d976"),
            4: QColor("#8b5e57"),
            5: QColor("#3b82f6"),
            6: QColor("#ff69b4"),
            7: QColor("#3f3a4d"),
        }
        self.setFixedHeight(112)

    def set_values(self, values):
        self.values = values[-30:]
        self.update()

    def set_background(self, color):
        self.background = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.background)

        rows = 3
        cols = 10
        radius = min(12, max(7, int((self.width() - 28) / (cols * 2 + (cols - 1) * 0.8))))
        gap_x = radius * 0.8
        gap_y = 8
        grid_width = cols * radius * 2 + (cols - 1) * gap_x
        grid_height = rows * radius * 2 + (rows - 1) * gap_y
        start_x = (self.width() - grid_width) / 2 + radius
        start_y = (self.height() - grid_height) / 2 + radius - 6

        painter.setPen(QPen(QColor("#334155"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for row in range(rows):
            for col in range(cols):
                cx = start_x + col * (radius * 2 + gap_x)
                cy = start_y + row * (radius * 2 + gap_y)
                painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

        for index, event in enumerate(self.values[-(rows * cols):]):
            row = index // cols
            col = index % cols
            cx = start_x + col * (radius * 2 + gap_x)
            cy = start_y + row * (radius * 2 + gap_y)
            self.draw_event(painter, event, cx, cy, radius)

    def draw_event(self, painter, event, cx, cy, radius):
        if isinstance(event, int):
            BallDisplay.draw_ball(self, painter, cx, cy, radius, self.ball_colors.get(event, QColor("#ffffff")))
            return

        if isinstance(event, tuple) and event[0] == "F":
            BallDisplay.draw_ball(self, painter, cx, cy, radius, QColor("#f8fafc"))
            painter.setPen(QColor("#ef4444"))
            font = QFont("Arial", max(9, radius))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                QRectF(cx - radius, cy - radius, radius * 2, radius * 2),
                Qt.AlignmentFlag.AlignCenter,
                str(event[1]),
            )
            return

        if isinstance(event, tuple) and event[0] == "F_PLUS":
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))
            painter.setPen(QColor("#ffffff"))
            font = QFont("Arial", max(8, int(radius * 0.85)))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                QRectF(cx - radius, cy - radius, radius * 2, radius * 2),
                Qt.AlignmentFlag.AlignCenter,
                f"+{event[1]}",
            )
            return

        if event == "P":
            painter.setPen(QPen(QColor("#93c5fd"), 2))
            painter.setBrush(QColor("#1d4ed8"))
            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))
            painter.setPen(QPen(QColor("#ffffff"), max(2, int(radius * 0.18))))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawLine(QPointF(cx - radius * 0.48, cy - radius * 0.22), QPointF(cx + radius * 0.32, cy - radius * 0.22))
            painter.drawLine(QPointF(cx + radius * 0.48, cy + radius * 0.22), QPointF(cx - radius * 0.32, cy + radius * 0.22))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#ffffff"))
            upper_arrow = QPolygonF([
                QPointF(cx + radius * 0.32, cy - radius * 0.50),
                QPointF(cx + radius * 0.62, cy - radius * 0.22),
                QPointF(cx + radius * 0.32, cy + radius * 0.06),
            ])
            lower_arrow = QPolygonF([
                QPointF(cx - radius * 0.32, cy - radius * 0.06),
                QPointF(cx - radius * 0.62, cy + radius * 0.22),
                QPointF(cx - radius * 0.32, cy + radius * 0.50),
            ])
            painter.drawPolygon(upper_arrow)
            painter.drawPolygon(lower_arrow)


class BreakDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.break_score = 0
        self.highest_breaks = [0, 0]

    def set_values(self, break_score, highest_breaks):
        self.break_score = break_score
        self.highest_breaks = highest_breaks[:]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#111827"))
        painter.setPen(QPen(QColor("#9ca3af"), 2))
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

        title_font = QFont("Arial", 42)
        score_font = QFont("Arial", 42)
        hb_font = QFont("Arial", 28)
        title_metrics = QFontMetrics(title_font)
        score_metrics = QFontMetrics(score_font)
        hb_metrics = QFontMetrics(hb_font)

        gap_between_break_and_score = 4
        hb_gap = 40
        title_height = title_metrics.height()
        score_height = score_metrics.height()
        center_y = self.height() / 2 - 20
        group_height = title_height + gap_between_break_and_score + score_height
        title_top = center_y - group_height / 2
        score_top = title_top + title_height + gap_between_break_and_score
        hb_top = score_top + score_height + hb_gap

        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(title_font)
        painter.drawText(
            QRectF(0, title_top, self.width(), title_height),
            Qt.AlignmentFlag.AlignCenter,
            "BREAK",
        )
        painter.setFont(score_font)
        painter.drawText(
            QRectF(0, score_top, self.width(), score_height),
            Qt.AlignmentFlag.AlignCenter,
            str(self.break_score),
        )
        painter.setFont(hb_font)
        painter.drawText(
            QRectF(0, hb_top, self.width(), hb_metrics.height()),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.highest_breaks[0]}     HB     {self.highest_breaks[1]}",
        )


class SnookerBoard(QWidget):
    def __init__(self):
        super().__init__()

        self.players = ["PLAYER 1", "PLAYER 2"]
        self.current = 0

        self.scores = [0, 0]
        self.frames = [0, 0]
        self.break_score = 0
        self.highest_breaks = [0, 0]

        self.reds = 15
        self.colors = {
            "yellow": 1,
            "green": 1,
            "brown": 1,
            "blue": 1,
            "pink": 1,
            "black": 1,
        }

        self.history = []
        self.pot_history = [[], []]
        self.undo_stack = []

        self.seconds = 0
        self.timer_paused = True
        self.foul_pending = False
        self.freeball_pending = False
        self.end_frame_pending = False
        self.status_player = None
        self.can_take_red = True
        self.color_allowed = False
        self.final_red_color_pending = False
        self.next_color_value = 2
        self.target_frames = 5
        self.controls_width = 300
        self.control_language = "EN"

        self.init_ui()
        self.start_timer()
        QApplication.instance().installEventFilter(self)

    def init_ui(self):
        self.setWindowTitle("Snooker Board")
        self.resize(1500, 850)

        self.setStyleSheet("""
            QWidget {
                background-color: #0b1020;
                color: white;
                font-family: Arial;
            }
            QLabel {
                background-color: #111827;
                color: white;
                border: 2px solid #9ca3af;
            }
            QPushButton {
                background-color: #1f2937;
                color: white;
                font-size: 22px;
                font-weight: bold;
                border: 2px solid #6b7280;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)

        main = QVBoxLayout()
        main.setSpacing(4)

        title = QLabel("IN PLAY")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(100)
        title.setStyleSheet("font-size: 44px; border: none; background: transparent; letter-spacing: 6px;")
        main.addWidget(title)

        board = QGridLayout()
        board.setSpacing(8)

        self.left_name = self.panel_label(self.players[0], 40)
        self.right_name = self.panel_label(self.players[1], 40)
        self.center_info = self.panel_label("", 32)

        self.left_frames = self.panel_label("0", 90)
        self.right_frames = self.panel_label("0", 90)

        self.break_title = self.panel_label("", 32)
        self.break_label = BreakDisplay()
        self.info_label = self.panel_label("", 32)
        self.points_title = self.panel_label("POINTS", 34)

        self.left_score = self.panel_label("0", 110)
        self.right_score = self.panel_label("0", 110)
        self.left_pots = PotHistoryDisplay()
        self.right_pots = PotHistoryDisplay()
        self.left_score_panel = self.score_panel(self.left_score, self.left_pots)
        self.right_score_panel = self.score_panel(self.right_score, self.right_pots)
        self.left_player_panel = self.player_column_panel(self.left_name, self.left_frames, self.left_score_panel)
        self.right_player_panel = self.player_column_panel(self.right_name, self.right_frames, self.right_score_panel)

        board.addWidget(self.left_player_panel, 0, 0, 4, 1)
        board.addWidget(self.center_info, 0, 1)
        board.addWidget(self.right_player_panel, 0, 2, 4, 1)

        board.addWidget(self.break_title, 1, 1)

        board.addWidget(self.break_label, 2, 1)

        board.addWidget(self.info_label, 3, 1)

        board.setColumnStretch(0, 4)
        board.setColumnStretch(1, 2)
        board.setColumnStretch(2, 4)
        board.setRowStretch(0, 1)
        board.setRowStretch(1, 1)
        board.setRowStretch(2, 3)
        board.setRowStretch(3, 1)

        main.addLayout(board, 1)

        self.history_label = QLabel("")
        self.history_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.history_label.setMinimumWidth(0)
        self.history_label.setFixedHeight(44)
        self.history_label.setStyleSheet("""
            font-size: 24px;
            background-color: white;
            color: black;
            padding: 6px;
            border: 2px solid #9ca3af;
        """)
        main.addWidget(self.history_label)

        self.balls_label = BallDisplay()
        self.balls_label.setFixedHeight(96)
        self.balls_label.setStyleSheet("""
            background-color: #050505;
            border: 2px solid #9ca3af;
        """)
        main.addWidget(self.balls_label)

        self.controls_panel = QWidget()
        self.controls_panel.setMaximumWidth(0)
        self.controls_panel.setMinimumWidth(0)
        self.controls_panel.leaveEvent = lambda event: self.hide_controls()
        self.controls_panel.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                border-left: 2px solid #475569;
            }
        """)

        controls = QVBoxLayout(self.controls_panel)
        controls.setContentsMargins(10, 10, 10, 10)
        controls.setSpacing(8)

        self.controls_title = QLabel()
        self.controls_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.controls_title.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        controls.addWidget(self.controls_title)

        self.language_btn = QPushButton()
        self.language_btn.clicked.connect(self.toggle_control_language)
        controls.addWidget(self.language_btn)

        score_buttons = QGridLayout()
        score_buttons.setSpacing(8)

        for value in range(1, 8):
            btn = QPushButton(f"+{value}")
            btn.clicked.connect(lambda _, v=value: self.add_score(v))
            score_buttons.addWidget(btn, (value - 1) // 2, (value - 1) % 2)

        self.foul_btn = QPushButton()
        self.foul_btn.setStyleSheet("""
            background-color: #7f1d1d;
            color: white;
            font-size: 22px;
            font-weight: bold;
            border: 2px solid #dc2626;
            border-radius: 8px;
            padding: 12px;
        """)
        self.foul_btn.clicked.connect(self.mark_foul)
        score_buttons.addWidget(self.foul_btn, 3, 1)

        self.red_plus_btn = QPushButton()
        self.red_plus_btn.clicked.connect(lambda: self.adjust_reds(1))
        score_buttons.addWidget(self.red_plus_btn, 4, 0)

        self.red_minus_btn = QPushButton()
        self.red_minus_btn.clicked.connect(lambda: self.adjust_reds(-1))
        score_buttons.addWidget(self.red_minus_btn, 4, 1)

        self.undo_btn = QPushButton()
        self.undo_btn.clicked.connect(self.undo)
        score_buttons.addWidget(self.undo_btn, 5, 0)

        self.switch_btn = QPushButton()
        self.switch_btn.clicked.connect(self.switch_player)
        score_buttons.addWidget(self.switch_btn, 5, 1)

        controls.addLayout(score_buttons)

        bottom = QVBoxLayout()
        bottom.setSpacing(8)

        self.name1_btn = QPushButton()
        self.name1_btn.clicked.connect(lambda: self.rename_player(0))
        bottom.addWidget(self.name1_btn)

        self.name2_btn = QPushButton()
        self.name2_btn.clicked.connect(lambda: self.rename_player(1))
        bottom.addWidget(self.name2_btn)

        self.target_frames_btn = QPushButton()
        self.target_frames_btn.clicked.connect(self.set_target_frames)
        bottom.addWidget(self.target_frames_btn)

        self.end_frame_btn = QPushButton()
        self.end_frame_btn.clicked.connect(self.confirm_end_frame)
        bottom.addWidget(self.end_frame_btn)

        self.new_btn = QPushButton()
        self.new_btn.clicked.connect(self.confirm_reset_frame)
        bottom.addWidget(self.new_btn)

        self.reset_match_btn = QPushButton()
        self.reset_match_btn.clicked.connect(self.confirm_reset_match)
        bottom.addWidget(self.reset_match_btn)

        self.full_btn = QPushButton()
        self.full_btn.clicked.connect(self.toggle_fullscreen)
        bottom.addWidget(self.full_btn)

        controls.addLayout(bottom)
        controls.addStretch(1)

        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addLayout(main, 1)
        root.addWidget(self.controls_panel)

        self.setMouseTracking(True)
        self.setLayout(root)
        self.create_end_frame_overlay()
        self.update_control_language()
        self.update_display()

    def panel_label(self, text, size):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"""
            font-size: {size}px;
            background-color: #111827;
            color: white;
            border: 2px solid #9ca3af;
            padding: 8px;
        """)
        return label

    def control_texts(self):
        texts = {
            "EN": {
                "language": "EN / DE: EN",
                "title": "CONTROLS",
                "foul": "F FOUL",
                "red_plus": "Red +1",
                "red_minus": "Red -1",
                "undo": "UNDO",
                "switch": "PLAYER",
                "rename_left": "Rename Left",
                "rename_right": "Rename Right",
                "set_frames": "Set Frames",
                "end_frame": "End Frame",
                "reset_frame": "Reset Frame",
                "reset_match": "Reset Match",
                "fullscreen": "Fullscreen",
                "set_frames_prompt": "Enter total frames:",
                "rename_player": "Rename Player",
                "rename_prompt": "Enter name:",
                "end_frame_confirm": "End this frame?",
                "reset_frame_confirm": "Reset the current frame?",
                "reset_match_confirm": "Reset the whole match?",
            },
            "DE": {
                "language": "EN / DE: DE",
                "title": "STEUERUNG",
                "foul": "F FOUL",
                "red_plus": "Rot +1",
                "red_minus": "Rot -1",
                "undo": "ZURÜECK",
                "switch": "SPIELER",
                "rename_left": "Links umbenennen",
                "rename_right": "Rechts umbenennen",
                "set_frames": "Frames setzen",
                "end_frame": "Frame beenden",
                "reset_frame": "Frame zurücksetzen",
                "reset_match": "Match zurücksetzen",
                "fullscreen": "Vollbild",
                "set_frames_prompt": "Gesamtzahl Frames:",
                "rename_player": "Spieler umbenennen",
                "rename_prompt": "Name eingeben:",
                "end_frame_confirm": "Diesen Frame beenden?",
                "reset_frame_confirm": "Aktuellen Frame zurücksetzen?",
                "reset_match_confirm": "Ganzes Match zurücksetzen?",
            },
        }
        return texts[self.control_language]

    def update_control_language(self):
        text = self.control_texts()
        self.language_btn.setText(text["language"])
        self.controls_title.setText(text["title"])
        self.foul_btn.setText(text["foul"])
        self.red_plus_btn.setText(text["red_plus"])
        self.red_minus_btn.setText(text["red_minus"])
        self.undo_btn.setText(text["undo"])
        self.switch_btn.setText(text["switch"])
        self.name1_btn.setText(text["rename_left"])
        self.name2_btn.setText(text["rename_right"])
        self.target_frames_btn.setText(text["set_frames"])
        self.end_frame_btn.setText(text["end_frame"])
        self.new_btn.setText(text["reset_frame"])
        self.reset_match_btn.setText(text["reset_match"])
        self.full_btn.setText(text["fullscreen"])

    def toggle_control_language(self):
        self.control_language = "DE" if self.control_language == "EN" else "EN"
        self.update_control_language()

    def score_panel(self, score_label, pot_display):
        panel = QWidget()
        panel.setObjectName("scorePanel")
        score_label.setStyleSheet("""
            font-size: 132px;
            background-color: transparent;
            color: white;
            border: none;
            padding: 8px;
        """)
        pot_display.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        layout.addWidget(score_label, 1)
        layout.addWidget(pot_display, 0)
        return panel

    def player_column_panel(self, name_label, frames_label, score_panel):
        panel = QWidget()
        panel.setObjectName("playerColumn")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        layout.addWidget(name_label, 1)
        layout.addWidget(frames_label, 1)
        layout.addWidget(score_panel, 4)
        return panel

    def create_end_frame_overlay(self):
        self.end_frame_overlay = QWidget(self)
        self.end_frame_overlay.setObjectName("endFrameOverlay")
        self.end_frame_overlay.setStyleSheet("""
            QWidget#endFrameOverlay {
                background-color: rgba(0, 0, 0, 170);
            }
            QLabel#endFramePrompt {
                background-color: #111827;
                color: #facc15;
                border: 5px solid #facc15;
                border-radius: 8px;
                font-size: 52px;
                font-weight: bold;
                padding: 38px 64px;
            }
        """)

        overlay_layout = QVBoxLayout(self.end_frame_overlay)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.addStretch(1)

        prompt_row = QHBoxLayout()
        prompt_row.addStretch(1)
        self.end_frame_prompt = QLabel("PRESS 3 TO END FRAME")
        self.end_frame_prompt.setObjectName("endFramePrompt")
        self.end_frame_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt_row.addWidget(self.end_frame_prompt)
        prompt_row.addStretch(1)

        overlay_layout.addLayout(prompt_row)
        overlay_layout.addStretch(1)

        self.end_frame_overlay.hide()

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def tick(self):
        if self.timer_paused:
            return
        self.seconds += 1
        self.update_timer()

    def update_timer(self):
        minutes = self.seconds // 60
        seconds = self.seconds % 60
        self.center_info.setText(f"{minutes:02d} {seconds:02d}\nMIN  SEC")
        timer_style = """
            font-size: 32px;
            background-color: #7f1d1d;
            color: white;
            border: 4px solid #ef4444;
            padding: 8px;
        """ if self.timer_paused else """
            font-size: 32px;
            background-color: #111827;
            color: white;
            border: 2px solid #9ca3af;
            padding: 8px;
        """
        self.center_info.setStyleSheet(timer_style)

    def save_state(self):
        self.undo_stack.append({
            "players": self.players[:],
            "current": self.current,
            "scores": self.scores[:],
            "frames": self.frames[:],
            "break_score": self.break_score,
            "highest_breaks": self.highest_breaks[:],
            "reds": self.reds,
            "colors": deepcopy(self.colors),
            "history": self.history[:],
            "pot_history": deepcopy(self.pot_history),
            "seconds": self.seconds,
            "timer_paused": self.timer_paused,
            "foul_pending": self.foul_pending,
            "freeball_pending": self.freeball_pending,
            "end_frame_pending": self.end_frame_pending,
            "status_player": self.status_player,
            "can_take_red": self.can_take_red,
            "color_allowed": self.color_allowed,
            "final_red_color_pending": self.final_red_color_pending,
            "next_color_value": self.next_color_value,
            "target_frames": self.target_frames,
        })

    def restore_state(self, state):
        self.players = state["players"][:]
        self.current = state["current"]
        self.scores = state["scores"][:]
        self.frames = state["frames"][:]
        self.break_score = state["break_score"]
        self.highest_breaks = state.get("highest_breaks", [state.get("highest_break", 0), 0])[:]
        self.reds = state["reds"]
        self.colors = deepcopy(state["colors"])
        self.history = state["history"][:]
        self.pot_history = deepcopy(state.get("pot_history", [[], []]))
        self.seconds = state["seconds"]
        self.timer_paused = state["timer_paused"]
        self.foul_pending = state["foul_pending"]
        self.freeball_pending = state["freeball_pending"]
        self.end_frame_pending = state["end_frame_pending"]
        self.status_player = state["status_player"]
        self.can_take_red = state["can_take_red"]
        self.color_allowed = state.get("color_allowed", False)
        self.final_red_color_pending = state.get("final_red_color_pending", False)
        self.next_color_value = state["next_color_value"]
        self.target_frames = state.get("target_frames", self.target_frames)

    def add_score(self, value):
        if self.foul_pending:
            if value == 1:
                self.adjust_reds(-1)
            elif value == 3:
                self.adjust_reds(1)
            elif 4 <= value <= 7:
                self.award_foul(value)
            return

        if self.freeball_pending:
            freeball_value = self.freeball_value()
            if value == freeball_value:
                self.save_state()
                self.scores[self.current] += freeball_value
                self.break_score += freeball_value
                self.update_highest_break()
                self.history.append(f"FB{freeball_value}")
                self.append_pot_event(self.current, freeball_value)
                self.freeball_pending = False
                self.status_player = None
                if self.reds > 0:
                    self.color_allowed = True
                elif self.final_red_color_pending:
                    self.final_red_color_pending = False
                    self.next_color_value = 2
                self.update_display()
            return

        if self.end_frame_pending:
            if value == 3:
                self.finish_frame_by_score()
            return

        if not self.is_legal_score(value):
            return

        self.save_state()
        self.apply_score(value)

        self.update_display()

    def mark_foul(self):
        self.save_state()

        if self.freeball_pending:
            self.clear_pending_actions()
        elif self.foul_pending:
            self.foul_pending = False
            self.freeball_pending = True
            self.status_player = self.current
        else:
            self.foul_pending = True
            self.freeball_pending = False
            self.end_frame_pending = False
            self.status_player = self.current

        self.update_display()

    def award_foul(self, value):
        if not self.foul_pending or not (4 <= value <= 7):
            return

        self.save_state()

        opponent = 1 - self.current
        self.scores[opponent] += value
        self.history.append(f"F:{value}")
        self.append_pot_event(self.current, ("F", value))
        self.append_pot_event(opponent, ("F_PLUS", value))

        self.break_score = 0
        self.current = opponent
        self.foul_pending = False
        self.freeball_pending = False
        self.end_frame_pending = False
        self.status_player = None
        self.color_allowed = False
        self.final_red_color_pending = False

        self.update_display()

    def switch_player(self):
        self.save_state()

        self.current = 1 - self.current
        self.break_score = 0
        self.history.append("P")
        self.color_allowed = False
        self.final_red_color_pending = False
        self.append_switch_marker(self.current)
        self.clear_pending_actions()

        self.update_display()

    def undo(self):
        if not self.undo_stack:
            return

        state = self.undo_stack.pop()
        self.restore_state(state)
        self.update_display()

    def new_frame(self):
        self.save_state()

        self.scores = [0, 0]
        self.break_score = 0
        self.reds = 15
        self.colors = {
            "yellow": 1,
            "green": 1,
            "brown": 1,
            "blue": 1,
            "pink": 1,
            "black": 1,
        }
        self.history = []
        self.pot_history = [[], []]
        self.seconds = 0
        self.timer_paused = False
        self.current = 0
        self.can_take_red = True
        self.color_allowed = False
        self.final_red_color_pending = False
        self.next_color_value = 2
        self.clear_pending_actions()

        self.update_display()

    def add_frame(self, player):
        self.save_state()
        self.frames[player] += 1
        self.complete_frame(player)

    def reset_match(self):
        self.save_state()
        self.frames = [0, 0]
        self.highest_breaks = [0, 0]
        self.reset_frame()
        self.update_display()

    def start_new_match(self):
        self.frames = [0, 0]
        self.highest_breaks = [0, 0]
        self.reset_frame()
        self.update_display()

    def reset_frame(self):
        self.scores = [0, 0]
        self.break_score = 0
        self.reds = 15
        self.colors = {
            "yellow": 1,
            "green": 1,
            "brown": 1,
            "blue": 1,
            "pink": 1,
            "black": 1,
        }
        self.history = []
        self.pot_history = [[], []]
        self.seconds = 0
        self.current = 0
        self.can_take_red = True
        self.color_allowed = False
        self.final_red_color_pending = False
        self.next_color_value = 2
        self.clear_pending_actions()

    def request_end_frame(self):
        self.save_state()
        self.clear_pending_actions()
        self.end_frame_pending = True
        self.status_player = self.current
        self.history.append("W")
        self.update_display()

    def confirm_end_frame(self):
        text = self.control_texts()
        if self.confirm_action(text["end_frame"], text["end_frame_confirm"]):
            self.finish_frame_by_score()

    def confirm_reset_frame(self):
        text = self.control_texts()
        if self.confirm_action(text["reset_frame"], text["reset_frame_confirm"]):
            self.new_frame()

    def confirm_reset_match(self):
        text = self.control_texts()
        if self.confirm_action(text["reset_match"], text["reset_match_confirm"]):
            self.reset_match()

    def confirm_action(self, title, message):
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def finish_frame_by_score(self):
        self.save_state()
        winner = 0 if self.scores[0] >= self.scores[1] else 1
        self.frames[winner] += 1
        self.complete_frame(winner)

    def complete_frame(self, winner):
        self.reset_frame()
        self.update_display()
        if self.frames[winner] >= self.match_winning_frames():
            message = QMessageBox(self)
            message.setWindowTitle("Match Finished")
            message.setIcon(QMessageBox.Icon.Information)
            message.setText(
                f"Congratulations {self.players[winner]}!\n"
                "You won the match.\n\n"
                "Highest Breaks:\n"
                f"{self.players[0]}: {self.highest_breaks[0]}\n"
                f"{self.players[1]}: {self.highest_breaks[1]}"
            )
            message.setStandardButtons(QMessageBox.StandardButton.Ok)
            message.setStyleSheet("QLabel { font-size: 24px; } QPushButton { font-size: 20px; padding: 8px 24px; }")
            message.exec()
            self.start_new_match()

    def match_winning_frames(self):
        return self.target_frames // 2 + 1

    def clear_pending_actions(self):
        self.foul_pending = False
        self.freeball_pending = False
        self.end_frame_pending = False
        self.status_player = None

    def append_pot_event(self, player, event):
        self.pot_history[player].append(event)
        self.pot_history[player] = self.pot_history[player][-30:]

    def append_switch_marker(self, player):
        if not any(self.pot_history):
            return
        for index in range(2):
            if self.pot_history[index] and self.pot_history[index][-1] == "P":
                self.pot_history[index].pop()
        self.append_pot_event(player, "P")

    def is_legal_score(self, value):
        if self.final_red_color_pending:
            return 2 <= value <= 7

        if self.reds > 0:
            if value == 1:
                return True
            return self.color_allowed and 2 <= value <= 7

        return value == self.next_color_value

    def apply_score(self, value):
        self.scores[self.current] += value
        self.break_score += value
        self.update_highest_break()
        self.history.append(str(value))
        self.append_pot_event(self.current, value)

        if self.final_red_color_pending:
            self.final_red_color_pending = False
            self.color_allowed = False
            self.next_color_value = 2
            return

        if self.reds > 0:
            if value == 1:
                self.reds -= 1
                self.color_allowed = True
                if self.reds == 0:
                    self.final_red_color_pending = True
                    self.next_color_value = 2
            else:
                self.color_allowed = False
            return

        self.remove_color(value)
        self.next_color_value = min(value + 1, 8)

    def adjust_reds(self, amount):
        self.save_state()
        self.reds = max(0, min(15, self.reds + amount))
        if self.reds > 0:
            self.can_take_red = True
            self.color_allowed = False
            self.final_red_color_pending = False
        else:
            self.color_allowed = False
            self.final_red_color_pending = False
            self.next_color_value = 2
        self.clear_pending_actions()
        self.update_display()

    def remove_color(self, value):
        color_by_value = {
            2: "yellow",
            3: "green",
            4: "brown",
            5: "blue",
            6: "pink",
            7: "black",
        }
        color = color_by_value.get(value)
        if color and self.colors[color] > 0:
            self.colors[color] = 0

    def remaining_points(self):
        if self.final_red_color_pending:
            return 27 + 7

        if self.reds > 0:
            pending_color = 7 if self.color_allowed else 0
            return self.reds * 8 + 27 + pending_color
        color_values = {
            "yellow": 2,
            "green": 3,
            "brown": 4,
            "blue": 5,
            "pink": 6,
            "black": 7,
        }
        return sum(color_values[color] for color, left in self.colors.items() if left)

    def freeball_value(self):
        if self.final_red_color_pending:
            return 7
        if self.reds > 0:
            return 1
        return self.next_color_value

    def score_difference(self):
        return abs(self.scores[0] - self.scores[1])

    def update_highest_break(self):
        self.highest_breaks[self.current] = max(self.highest_breaks[self.current], self.break_score)

    def toggle_timer_pause(self):
        self.save_state()
        self.timer_paused = not self.timer_paused
        self.history.append("C")
        self.update_display()

    def set_target_frames(self):
        text = self.control_texts()
        frames, ok = QInputDialog.getInt(
            self,
            text["set_frames"],
            text["set_frames_prompt"],
            self.target_frames,
            1,
            99,
            1,
        )
        if ok:
            self.save_state()
            self.target_frames = frames
            self.update_display()

    def rename_player(self, index):
        text = self.control_texts()
        name, ok = QInputDialog.getText(self, text["rename_player"], text["rename_prompt"])
        if ok and name.strip():
            self.save_state()
            self.players[index] = name.strip().upper()
            self.update_display()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def update_display(self):
        self.left_name.setText(self.players[0])
        self.right_name.setText(self.players[1])

        left_status = self.player_status(0)
        right_status = self.player_status(1)
        self.left_name.setText(f"{self.players[0]}{left_status}")
        self.right_name.setText(f"{self.players[1]}{right_status}")

        self.left_frames.setText(str(self.frames[0]))
        self.right_frames.setText(str(self.frames[1]))
        self.break_title.setText(f"FRAMES\n({self.target_frames})")

        self.left_score.setText(str(self.scores[0]))
        self.right_score.setText(str(self.scores[1]))
        self.left_pots.set_values(self.pot_history[0])
        self.right_pots.set_values(self.pot_history[1])

        self.break_label.set_values(self.break_score, self.highest_breaks)
        self.info_label.setText(
            f"REMAINING: {self.remaining_points()}\n"
            f"DIFFERENCE: {self.score_difference()}"
        )

        self.history_label.setText(self.history_text())

        self.balls_label.set_counts(self.reds, self.colors)

        active_name_style = """
            font-size: 40px;
            background-color: #172554;
            color: #facc15;
            border: none;
            border-bottom: 2px solid #9ca3af;
            padding: 8px;
        """

        normal_name_style = """
            font-size: 40px;
            background-color: #111827;
            color: white;
            border: none;
            border-bottom: 2px solid #9ca3af;
            padding: 8px;
        """

        status_name_style = """
            font-size: 40px;
            background-color: #7f1d1d;
            color: white;
            border: none;
            border-bottom: 2px solid #9ca3af;
            padding: 8px;
        """

        self.left_name.setStyleSheet(self.player_label_style(0, active_name_style, normal_name_style, status_name_style))
        self.right_name.setStyleSheet(self.player_label_style(1, active_name_style, normal_name_style, status_name_style))
        self.left_frames.setStyleSheet(self.player_panel_style(0, 90))
        self.right_frames.setStyleSheet(self.player_panel_style(1, 90))
        self.left_score_panel.setStyleSheet(self.player_score_panel_style(0))
        self.right_score_panel.setStyleSheet(self.player_score_panel_style(1))
        self.left_player_panel.setStyleSheet(self.player_column_style(0))
        self.right_player_panel.setStyleSheet(self.player_column_style(1))
        self.left_pots.set_background("#0b1020")
        self.right_pots.set_background("#0b1020")

        self.update_end_frame_overlay()
        self.update_timer()

    def history_text(self):
        recent = ", ".join(self.history[-18:])
        width = max(80, self.history_label.width() - 20)
        metrics = QFontMetrics(self.history_label.font())
        return metrics.elidedText(recent, Qt.TextElideMode.ElideLeft, width)

    def player_label_style(self, player, active_style, normal_style, status_style):
        if self.status_player == player and (self.foul_pending or self.freeball_pending):
            return status_style
        if self.current == player:
            return active_style
        return normal_style

    def player_panel_style(self, player, size):
        background = "#111827"
        color = "white"
        return f"""
            font-size: {size}px;
            background-color: {background};
            color: {color};
            border: none;
            border-bottom: 2px solid #9ca3af;
            padding: 8px;
        """

    def player_score_panel_style(self, player):
        background = "#111827"
        return f"""
            QWidget#scorePanel {{
                background-color: {background};
                border: none;
            }}
        """

    def player_column_style(self, player):
        border = "#facc15" if self.current == player else "white"
        width = 4 if self.current == player else 2
        return f"""
            QWidget#playerColumn {{
                background-color: #111827;
                border: {width}px solid {border};
            }}
        """

    def player_status(self, player):
        if self.status_player != player:
            return ""
        if self.foul_pending:
            return "\nFOUL"
        if self.freeball_pending:
            return "\nFREEBALL"
        if self.end_frame_pending:
            return "\nPRESS 3 END"
        return ""

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseMove and self.isVisible():
            local = self.mapFromGlobal(event.globalPosition().toPoint())
            if self.rect().contains(local) and local.x() >= self.width() - 12:
                self.show_controls()
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "end_frame_overlay"):
            self.end_frame_overlay.setGeometry(self.rect())

    def update_end_frame_overlay(self):
        if self.end_frame_pending:
            self.end_frame_overlay.setGeometry(self.rect())
            self.end_frame_overlay.show()
            self.end_frame_overlay.raise_()
        else:
            self.end_frame_overlay.hide()

    def show_controls(self):
        if self.controls_panel.maximumWidth() >= self.controls_width:
            return
        self.animate_controls(self.controls_width)

    def hide_controls(self):
        if self.controls_panel.maximumWidth() == 0:
            return
        self.animate_controls(0)

    def animate_controls(self, width):
        self.controls_animation = QPropertyAnimation(self.controls_panel, b"maximumWidth")
        self.controls_animation.setDuration(180)
        self.controls_animation.setStartValue(self.controls_panel.maximumWidth())
        self.controls_animation.setEndValue(width)
        self.controls_animation.start()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if Qt.Key.Key_1 <= key <= Qt.Key.Key_7:
            self.add_score(key - Qt.Key.Key_0)

        elif key == Qt.Key.Key_E:
            self.undo()

        elif key == Qt.Key.Key_P:
            self.switch_player()

        elif key == Qt.Key.Key_F:
            self.mark_foul()

        elif key == Qt.Key.Key_W:
            self.request_end_frame()

        elif key == Qt.Key.Key_C:
            self.toggle_timer_pause()

        elif key == Qt.Key.Key_V:
            self.toggle_fullscreen()

        elif key == Qt.Key.Key_F11:
            self.toggle_fullscreen()

        elif key == Qt.Key.Key_Escape:
            self.showNormal()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnookerBoard()
    window.show()
    sys.exit(app.exec())
