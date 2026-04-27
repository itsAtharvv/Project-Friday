import sys

import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QTimer, QObject, QRectF, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QBrush, QFont, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class Signals(QObject):
    show_ui = pyqtSignal(str)
    hide_ui = pyqtSignal()
    set_text = pyqtSignal(str)


signals = Signals()

STATE_COLORS = {
    "idle": QColor(24, 95, 165),
    "listening": QColor(55, 138, 221),
    "processing": QColor(186, 117, 23),
    "speaking": QColor(29, 158, 117),
    "done": QColor(60, 52, 137),
    "error": QColor(162, 45, 45),
}

STATE_LABELS = {
    "idle": "STANDBY",
    "listening": "LISTENING",
    "processing": "PROCESSING",
    "speaking": "FRIDAY",
    "done": "DONE",
    "error": "ERROR",
}

BAR_COUNT = 48


class VisualizerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.state = "idle"
        self.bars = [0.0] * BAR_COUNT
        self.t = 0.0
        self._audio_energy = 0.0
        self._stream = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

    def set_state(self, state: str):
        self.state = state
        if state == "listening":
            self._start_mic()
        else:
            self._stop_mic()
            
        if state in ["listening", "processing", "speaking"]:
            if not self.timer.isActive():
                self.timer.start(33)
        self.update()

    def _start_mic(self):
        try:
            self._stream = sd.InputStream(
                samplerate=16000,
                channels=1,
                dtype="float32",
                blocksize=512,
                callback=self._audio_callback,
            )
            self._stream.start()
        except Exception:
            pass

    def _stop_mic(self):
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        self._audio_energy = 0.0

    def _audio_callback(self, indata, frames, time, status):
        energy = float(np.sqrt(np.mean(indata**2)))
        self._audio_energy = min(energy * 300, 1.0)

    def _target(self, i: int) -> float:
        mid = BAR_COUNT / 2
        dist = abs(i - mid) / mid
        t = self.t
        s = self.state

        if s == "idle":
            return 3.0

        if s == "listening":
            e = self._audio_energy
            wave = np.sin(t * 4 + i * 0.4) * (e * 50 + 8)
            return max(3, wave)

        if s == "processing":
            return 6 + np.sin(t * 2.5 + i * 0.5) * 12 + np.sin(t * 6 + i) * 6

        if s == "speaking":
            wave = np.sin(t * 5 + i * 0.35) * (1 - dist * 0.4)
            return max(3, 18 + wave * 30)

        if s == "done":
            return max(0, self.bars[i] * 0.85)

        if s == "error":
            return 3.0

        return 3

    def _tick(self):
        self.t += 0.05
        active = False
        for i in range(BAR_COUNT):
            target = self._target(i)
            self.bars[i] += (target - self.bars[i]) * 0.2
            if abs(self.bars[i] - target) > 0.05:
                active = True
        self.update()
        
        if self.state in ["idle", "done", "error"] and not active:
            if self.timer.isActive():
                self.timer.stop()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cy = h / 2

        color = STATE_COLORS.get(self.state, QColor(55, 138, 221))

        gap = 3
        bar_w = (w - (BAR_COUNT - 1) * gap) / BAR_COUNT

        for i in range(BAR_COUNT):
            bh = max(2.0, self.bars[i])
            x = i * (bar_w + gap)

            p.setOpacity(0.9)
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(QRectF(x, cy - bh / 2, bar_w, bh), 2, 2)

            p.setOpacity(0.2)
            p.drawRoundedRect(QRectF(x, cy + bh / 2 + 2, bar_w, bh * 0.35), 2, 2)

        p.setOpacity(1.0)
        p.end()


class FridayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(520, 180)

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() // 2 - 260, screen.height() - 240)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        self.status_label = QLabel("STANDBY")
        self.status_label.setFont(QFont("Consolas", 11))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #185FA5; letter-spacing: 3px;")

        self.viz = VisualizerWidget()
        self.viz.setFixedHeight(80)

        self.text_label = QLabel("")
        self.text_label.setFont(QFont("Consolas", 9))
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet("color: #444455;")
        self.text_label.setWordWrap(True)

        layout.addWidget(self.status_label)
        layout.addWidget(self.viz)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

        signals.show_ui.connect(self.on_show)
        signals.hide_ui.connect(self.on_hide)
        signals.set_text.connect(self.on_set_text)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(8, 8, 16, 230)))
        p.setPen(QPen(QColor(55, 138, 221, 40), 1))
        p.drawRoundedRect(QRectF(self.rect()), 16, 16)

    @pyqtSlot(str)
    def on_show(self, state: str):
        color = STATE_COLORS.get(state, QColor(55, 138, 221))
        hex_color = color.name()
        self.status_label.setText(STATE_LABELS.get(state, state))
        self.status_label.setStyleSheet(f"color: {hex_color}; letter-spacing: 3px;")
        self.viz.set_state(state)
        self.show()

    @pyqtSlot()
    def on_hide(self):
        self.viz.set_state("done")
        QTimer.singleShot(1000, self.hide)

    @pyqtSlot(str)
    def on_set_text(self, text: str):
        self.text_label.setText(text)


def run_app():
    app = QApplication(sys.argv)
    window = FridayWindow()
    app.exec()
