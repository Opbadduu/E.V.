import os
import sys
import math
import threading
import numpy as np
from PIL import Image

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPixmap, QImage,
    QRadialGradient, QConicalGradient,
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel, QFrame
)

from core.speaker import speak
from core.listener import listen
from main import process_command
from modules.notes import get_pending_tasks


class WorkerSignals(QObject):
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(str)


class Wave:
    """A single expanding ripple ring. Born at the edge of the rotating
    ring (start_radius) and dies at the farthest corner of the screen
    (max_radius), fading linearly from a low starting opacity to zero."""
    __slots__ = ("radius", "start_radius", "max_radius", "speed", "color", "width")

    def __init__(self, start_radius, max_radius, speed, color, width):
        self.radius = start_radius
        self.start_radius = start_radius
        self.max_radius = max_radius
        self.speed = speed
        self.color = color
        self.width = width

    def step(self):
        self.radius += self.speed

    def alpha_fraction(self):
        """1.0 at start_radius, 0.0 at max_radius, linear in between."""
        span = self.max_radius - self.start_radius
        if span <= 0:
            return 0.0
        progress = (self.radius - self.start_radius) / span
        return max(0.0, 1.0 - progress)

    def is_dead(self):
        return self.radius >= self.max_radius


class EVSpiderGUI(QWidget):
    # ---- Tunables -------------------------------------------------
    LOGO_OPACITY = 0.30          # true 30% opacity emblem
    LOGO_DISPLAY_SIZE = 210      # px, so the rotating ring sits just outside it

    RING_RADIUS = 128            # fixed radius of the Alexa-style spinning ring
    RING_WIDTH = 5
    RING_ALPHA = 205             # ring stays vivid — it's the focal indicator
    RING_ROTATE_SPEED = {        # degrees/frame, per state
        "IDLE": 0.55,
        "LISTENING": 2.6,
        "PROCESSING": 3.4,
    }

    WAVE_START_OPACITY = 0.20    # <-- waves start at 20% alpha ...
    WAVE_END_OPACITY = 0.0       # <-- ... and fade to 0% at the far edge
    WAVE_LINE_WIDTH = 1.4
    WAVE_SPAWN_MS = {            # how often a new ring spawns, per state
        "IDLE": 900,
        "LISTENING": 380,
        "PROCESSING": 260,
    }
    WAVE_SPEED = {               # px/frame outward travel, per state
        "IDLE": 0.9,
        "LISTENING": 1.6,
        "PROCESSING": 2.1,
    }
    # -----------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self.setWindowTitle("E.V. // SPIDER-VERSE INTERFACE")
        self.resize(780, 880)
        self.setMinimumSize(700, 800)

        # Miles Morales Red / Gold / White palette
        self.COLOR_BG = QColor(8, 8, 10)
        self.COLOR_RED = QColor(230, 20, 40)
        self.COLOR_GOLD = QColor(255, 178, 40)
        self.COLOR_WHITE = QColor(245, 245, 255)
        self.COLOR_CYAN = QColor(0, 229, 255)
        self.COLOR_DARK_CARD = "rgba(15, 15, 20, 230)"

        self.anim_phase = 0.0
        self.anim_state = "IDLE"  # IDLE, LISTENING, PROCESSING
        self.waves = []
        self._ms_since_last_spawn = 0
        self.rotation_angle = 0.0     # drives the spinning Alexa-style ring
        self._logo_pixmap = None      # raw, unscaled RGBA pixmap, LOGO_OPACITY baked in

        self.signals = WorkerSignals()
        self.signals.log_signal.connect(self.log_message)
        self.signals.status_signal.connect(self.update_status)

        self.init_ui()
        self.load_logo()

        # Animation Timer (~60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

        # Startup Thread
        threading.Thread(target=self.startup_sequence, daemon=True).start()

    # ---------------------------------------------------------------
    # UI construction
    # ---------------------------------------------------------------
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 25)
        main_layout.setSpacing(15)

        # --- Top Status Header ---
        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"background-color: {self.COLOR_DARK_CARD}; border: 1px solid #E61428; border-radius: 12px;"
        )
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 12, 20, 12)

        title_label = QLabel("🕷️ E.V. PROTOCOL ")
        title_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #E61428; border: none; background: transparent;")

        self.status_label = QLabel("SYSTEM ONLINE")
        self.status_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #00FF99; border: none; background: transparent;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        main_layout.addWidget(header_frame)

        # --- Center stage for logo + waves (transparent spacer widget) ---
        self.stage = QLabel()
        self.stage.setFixedHeight(340)
        self.stage.setStyleSheet("background: transparent;")
        main_layout.addWidget(self.stage)

        # --- Terminal Chat Display ---
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 11))
        self.chat_display.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {self.COLOR_DARK_CARD};
                color: #F8FAFC;
                border: 1px solid #2A1015;
                border-radius: 12px;
                padding: 12px;
            }}
            """
        )
        main_layout.addWidget(self.chat_display, stretch=1)

        # --- Bottom Command Input Section ---
        input_frame = QFrame()
        input_frame.setFixedHeight(70)
        input_frame.setStyleSheet(
            f"background-color: {self.COLOR_DARK_CARD}; border: 1px solid #E61428; border-radius: 14px;"
        )
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(10)

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Type your command here and press Enter...")
        self.cmd_input.setFont(QFont("Consolas", 11))
        self.cmd_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: 1px solid #E61428;
                border-radius: 8px;
                padding: 10px 14px;
            }
            QLineEdit:focus {
                border: 1px solid #00E5FF;
            }
            """
        )
        self.cmd_input.returnPressed.connect(self.on_send_text)

        send_btn = QPushButton("SEND")
        send_btn.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        send_btn.setMinimumHeight(40)
        send_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #E61428;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0px 20px;
            }
            QPushButton:hover {
                background-color: #FF2E43;
            }
            """
        )
        send_btn.clicked.connect(self.on_send_text)

        mic_btn = QPushButton("🎙️ VOICE")
        mic_btn.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        mic_btn.setMinimumHeight(40)
        mic_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0B0E14;
                color: #00E5FF;
                border: 1px solid #00E5FF;
                border-radius: 8px;
                padding: 0px 16px;
            }
            QPushButton:hover {
                background-color: #1A2638;
            }
            """
        )
        mic_btn.clicked.connect(self.on_voice_click)

        input_layout.addWidget(self.cmd_input)
        input_layout.addWidget(send_btn)
        input_layout.addWidget(mic_btn)

        main_layout.addWidget(input_frame)

    # ---------------------------------------------------------------
    # Logo
    # ---------------------------------------------------------------
    LOGO_CANDIDATES = ("logo.png", "logo.jpg", "logo.jpeg", "logo.jfif", "logo.webp")

    def load_logo(self):
        """Loads the spider emblem and bakes in LOGO_OPACITY (true low-opacity
        emblem). Tries several filenames, and if the source has no real alpha
        channel (a flattened export with a plain/checker background instead of
        transparency) it auto-strips that background so no gray box shows up
        behind the spider."""
        path = next((p for p in self.LOGO_CANDIDATES if os.path.exists(p)), None)
        if path is None:
            self._logo_pixmap = None
            return

        try:
            img = Image.open(path).convert("RGBA")
            img = self._ensure_transparent(img)

            alpha = img.split()[3]
            alpha = alpha.point(lambda p: int(p * self.LOGO_OPACITY))
            img.putalpha(alpha)

            qim = QImage(img.tobytes("raw", "RGBA"), img.size[0], img.size[1], QImage.Format.Format_RGBA8888)
            self._logo_pixmap = QPixmap.fromImage(qim.copy())
        except Exception:
            self._logo_pixmap = None

    @staticmethod
    def _ensure_transparent(img: Image.Image) -> Image.Image:
        """If the image already carries real transparency, leave it alone.
        Otherwise (e.g. a JPEG/JFIF export with a flattened white/gray/checker
        backdrop baked into the pixels) strip that plain background out and
        decontaminate the edge colors so there's no gray halo."""
        arr = np.array(img).astype(np.float32)
        existing_alpha = arr[..., 3]

        # Real transparency already present (varies meaningfully) -> keep as is.
        if existing_alpha.std() > 5:
            return img

        rgb = arr[..., :3]
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        sat = mx - mn
        brightness = (r + g + b) / 3.0

        # Background = low-saturation (grayscale) AND reasonably bright
        neutral = 1.0 - np.clip(sat / 22.0, 0, 1)
        light = np.clip((brightness - 110.0) / 70.0, 0, 1)
        bg_amount = neutral * light
        alpha = np.clip(1.0 - bg_amount, 0, 1)

        # Decontaminate edge pixels so no light-gray fringe survives
        bg_est = 228.0
        a_safe = np.clip(alpha, 0.12, 1.0)[..., None]
        decontam = np.clip((rgb - (1 - a_safe) * bg_est) / a_safe, 0, 255)

        out = np.dstack([decontam.astype(np.uint8), (alpha * 255).astype(np.uint8)])
        return Image.fromarray(out, "RGBA")

    def stage_center(self):
        return self.stage.geometry().center()

    # ---------------------------------------------------------------
    # Painting
    # ---------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), self.COLOR_BG)

        center = self.stage_center()

        # 1. Expanding wave rings, born at the spinning ring's edge, fading
        #    from WAVE_START_OPACITY down to 0 by the farthest screen corner.
        for wave in self.waves:
            frac = wave.alpha_fraction()
            if frac <= 0:
                continue
            opacity = self.WAVE_END_OPACITY + (self.WAVE_START_OPACITY - self.WAVE_END_OPACITY) * frac
            c = QColor(wave.color)
            c.setAlpha(int(255 * opacity))
            pen = QPen(c, wave.width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            r = int(wave.radius)
            painter.drawEllipse(center, r, r)

        # 2. Soft ambient glow behind the logo (very low intensity radial gradient)
        glow_radius = self.RING_RADIUS + 25 + math.sin(self.anim_phase * 0.6) * 5
        gradient = QRadialGradient(QPointF(center), glow_radius)
        glow_color = self._current_state_color()
        c0 = QColor(glow_color)
        c0.setAlpha(26)
        c1 = QColor(glow_color)
        c1.setAlpha(0)
        gradient.setColorAt(0.0, c0)
        gradient.setColorAt(1.0, c1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(center, int(glow_radius), int(glow_radius))

        # 3. Alexa-style spinning ring: a conical (angular) gradient that
        #    rotates continuously around the logo, cycling red -> gold ->
        #    white -> red like a chasing light band.
        self._draw_spinning_ring(painter, center)

        # 4. Logo emblem, centered, baked-in low opacity, on top of everything
        if self._logo_pixmap is not None:
            size = self.LOGO_DISPLAY_SIZE
            scaled = self._logo_pixmap.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(
                center.x() - scaled.width() // 2,
                center.y() - scaled.height() // 2,
                scaled,
            )
        else:
            painter.setPen(QPen(QColor(230, 20, 40, 90)))
            painter.setFont(QFont("Consolas", 13))
            painter.drawText(
                center.x() - 150, center.y(),
                "🕷️  [logo.png not found in project root]"
            )

    def _draw_spinning_ring(self, painter, center):
        gradient = QConicalGradient(QPointF(center), self.rotation_angle)
        red = QColor(self.COLOR_RED)
        gold = QColor(self.COLOR_GOLD)
        white = QColor(self.COLOR_WHITE)
        for c in (red, gold, white):
            c.setAlpha(self.RING_ALPHA)
        gradient.setColorAt(0.0, red)
        gradient.setColorAt(0.33, gold)
        gradient.setColorAt(0.66, white)
        gradient.setColorAt(1.0, red)

        pen = QPen(QBrush(gradient), self.RING_WIDTH)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, self.RING_RADIUS, self.RING_RADIUS)

    def _current_state_color(self):
        if self.anim_state == "LISTENING":
            return self.COLOR_CYAN
        elif self.anim_state == "PROCESSING":
            return self.COLOR_GOLD
        return self.COLOR_RED

    # ---------------------------------------------------------------
    # Animation loop
    # ---------------------------------------------------------------
    def animate(self):
        self.anim_phase += 0.05

        # spin the Alexa-style ring; speed depends on state
        self.rotation_angle = (
            self.rotation_angle + self.RING_ROTATE_SPEED.get(self.anim_state, 0.55)
        ) % 360.0

        # spawn new waves at a rate depending on current state
        interval = self.WAVE_SPAWN_MS.get(self.anim_state, 900)
        self._ms_since_last_spawn += 16
        if self._ms_since_last_spawn >= interval:
            self._ms_since_last_spawn = 0
            self._spawn_wave()

        # advance existing waves
        speed = self.WAVE_SPEED.get(self.anim_state, 0.9)
        for wave in self.waves:
            wave.speed = speed
            wave.step()
        self.waves = [w for w in self.waves if not w.is_dead()]

        self.update()

    def _farthest_corner_distance(self, center):
        """Distance from center to the single farthest point on screen —
        this is where a wave's opacity must have decayed to exactly 0."""
        w, h = max(self.width(), 1), max(self.height(), 1)
        dx = max(center.x(), w - center.x())
        dy = max(center.y(), h - center.y())
        return math.hypot(dx, dy)

    def _spawn_wave(self):
        center = self.stage_center()
        max_r = self._farthest_corner_distance(center)
        color = self._current_state_color()
        self.waves.append(
            Wave(
                start_radius=self.RING_RADIUS,   # waves are born at the ring's edge
                max_radius=max_r,                # ...and die at the farthest corner
                speed=self.WAVE_SPEED.get(self.anim_state, 0.9),
                color=color,
                width=self.WAVE_LINE_WIDTH,
            )
        )

    # ---------------------------------------------------------------
    # Chat / status plumbing (unchanged behavior)
    # ---------------------------------------------------------------
    def log_message(self, sender: str, text: str):
        self.chat_display.append(f"<b>[{sender}]</b>: {text}\n")

    def update_status(self, status: str):
        if status == "LISTENING":
            self.anim_state = "LISTENING"
            self.status_label.setText("● LISTENING...")
            self.status_label.setStyleSheet("color: #00E5FF; border: none; background: transparent;")
        elif status == "PROCESSING":
            self.anim_state = "PROCESSING"
            self.status_label.setText("● PROCESSING...")
            self.status_label.setStyleSheet("color: #FFB000; border: none; background: transparent;")
        else:
            self.anim_state = "IDLE"
            self.status_label.setText("SYSTEM ONLINE")
            self.status_label.setStyleSheet("color: #00FF99; border: none; background: transparent;")

    def startup_sequence(self):
        self.signals.log_signal.emit("🤖 E.V.", "hey boss, what's to build today?")
        speak("hey boss, what's to build today?")

        pending = get_pending_tasks()
        if pending.startswith("You have") and "no pending tasks" not in pending:
            self.signals.log_signal.emit("📋 SYSTEM", pending)
            speak("just a reminder: You have pending tasks on your list")

    def handle_command(self, text: str):
        if not text.strip():
            return

        self.signals.log_signal.emit("💬 YOU", text)
        self.signals.status_signal.emit("PROCESSING")

        response = process_command(text)
        if response:
            self.signals.log_signal.emit("🤖 E.V.", response)
            speak(response)

        self.signals.status_signal.emit("IDLE")

    def on_send_text(self):
        text = self.cmd_input.text().strip()
        if text:
            self.cmd_input.clear()
            threading.Thread(target=self.handle_command, args=(text,), daemon=True).start()

    def on_voice_click(self):
        def voice_worker():
            self.signals.status_signal.emit("LISTENING")
            cmd = listen()
            if cmd:
                self.handle_command(cmd)
            else:
                self.signals.status_signal.emit("IDLE")

        threading.Thread(target=voice_worker, daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = EVSpiderGUI()
    gui.show()
    sys.exit(app.exec())