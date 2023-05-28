from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QProgressBar, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QIcon
import random
import colorsys
import time
import os
import sys
import signal
import darkdetect
import argparse

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Load funny messages from a file
with open(resource_path('messages.txt'), 'r') as f:
    messages = [line.strip() for line in f.readlines()]

def random_position_on_screen(edge_buffer=300):
    """Return a random position on the screen for a window."""
    screen = QApplication.primaryScreen().availableGeometry()
    x = random.randint(edge_buffer, screen.width() - edge_buffer)
    y = random.randint(edge_buffer, screen.height() - edge_buffer)
    return x, y

def make_rainbow(speed):
    """Create a function that generates smooth rainbow colors based on time and speed."""
    def rainbow():
        """Return the current color in the rainbow."""
        now = time.time()
        hue = (now * speed) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return QColor(r, g, b)
    return rainbow

class MovingProgressBar(QMainWindow):
    def __init__(self, movement_speed, initial_position, initial_direction):
        super().__init__()
        self.setWindowTitle("Loading...")
        self.message = random.choice(messages)

        # set icon to infinity symbol depending on the theme
        if darkdetect.isDark():
            self.setWindowIcon(QIcon(resource_path('icon_dark.svg')))
        else:
            self.setWindowIcon(QIcon(resource_path('icon_light.svg')))

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(random.randint(100, 1000))

        self.label = QLabel(self.message)

        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.rainbow = make_rainbow(random.uniform(0.5, 2.0))
        self.movement_speed = movement_speed
        self.direction = initial_direction
        initial_position = self.clip_to_screen(initial_position)
        self.setGeometry(*initial_position, 300, 100)

        self.timer_move_window = QTimer(self)
        self.timer_move_window.timeout.connect(self.move_window_func)
        self.timer_move_window.setInterval(10)
        self.timer_move_window.start()

        self.timer_progress = QTimer(self)
        self.timer_progress.timeout.connect(self.progress_func)
        self.timer_progress.start(self.get_progress_interval())

        self.timer_rainbow = QTimer(self)
        self.timer_rainbow.timeout.connect(self.rainbow_func)

        self.corner_hit = 0
        self.last_corner = None
        windows.append(self)

    def destroy(self, destroyWindow: bool = ..., destroySubWindows: bool = ...):
        # stop timers
        self.timer_move_window.stop()
        self.timer_progress.stop()
        self.timer_rainbow.stop()
        # remove from list of windows
        windows.remove(self)
        return super().destroy(destroyWindow, destroySubWindows)

    def is_at_corner(self, tolerance=10):
        """Return True if the window is at a corner."""
        screen = QApplication.primaryScreen().availableGeometry()
        screen_width, screen_height = screen.width(), screen.height()
        window_width, window_height = self.frameGeometry().width(), self.frameGeometry().height()
        x, y = self.x(), self.y()
        top_left = (x <= tolerance and y <= tolerance)
        top_right = (x >= screen_width - window_width - tolerance and y <= tolerance)
        bottom_left = (x <= tolerance and y >= screen_height - window_height - tolerance)
        bottom_right = (x >= screen_width - window_width - tolerance and y >= screen_height - window_height - tolerance)
        corner_index = [top_left, top_right, bottom_left, bottom_right].index(True) if any([top_left, top_right, bottom_left, bottom_right]) else None

        if (corner_index is not None and corner_index != self.last_corner):
            self.last_corner = corner_index
            self.corner_hit += 1
            return True
        return False

    def clip_to_screen(self, position):
        """Clip a position to the screen."""
        screen = QApplication.primaryScreen().availableGeometry()
        x, y = position
        x = max(0, min(x, screen.width() - self.frameGeometry().width()))
        y = max(0, min(y, screen.height() - self.frameGeometry().height()))
        return x, y

    def get_progress_interval(self):
        return random.uniform(10, 100)

    def rainbow_func(self):
        """Set the color of the progress bar."""
        self.progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {self.rainbow().name()}; }}")
        # restart the timer
        self.timer_rainbow.start(10)

    def progress_func(self):
        """Update the progress bar."""
        progress = self.progress_bar.value()
        if progress >= self.progress_bar.maximum():
            self.timer_progress.stop()
            if not self.corner_hit:
                # destroy the window
                self.close()
            else:
              # wait a few seconds before destroying the window
              QTimer.singleShot(3000, self.close)
            return
        self.progress_bar.setValue(progress + random.randint(0, 5))
        # restart the timer
        self.timer_progress.start(self.get_progress_interval())

    def move_window_func(self):
        x, y = self.x(), self.y()
        dx, dy = self.direction
        window_width, window_height = self.frameGeometry().width(), self.frameGeometry().height()
        screen_width, screen_height = QApplication.primaryScreen().availableGeometry().width(), QApplication.primaryScreen().availableGeometry().height()

        # update corner hit
        if self.is_at_corner():
            # increase speed
            self.movement_speed *= 2
            self.timer_rainbow.start()

        if x + dx <= 0 or x + dx >= screen_width - window_width:
            dx = -dx
        if y + dy <= 0 or y + dy >= screen_height - window_height:
            dy = -dy

        x += dx * self.movement_speed
        y += dy * self.movement_speed
        self.direction = (dx, dy)

        x, y = self.clip_to_screen((x, y))

        self.move(x, y)

windows = []

def create_moving_progress_bar():
    initial_position = random_position_on_screen()
    initial_direction = (random.uniform(3, 6), random.uniform(3, 6))
    # randomly invert either the x or y direction
    if random.choice([True, False]):
        initial_direction = (-initial_direction[0], initial_direction[1])
    if random.choice([True, False]):
        initial_direction = (initial_direction[0], -initial_direction[1])
    movement_speed = random.uniform(0.5, 1.0)
    new_win = MovingProgressBar(movement_speed, initial_position, initial_direction)
    if app.activeWindow() is None:
        new_win.setAttribute(Qt.WA_ShowWithoutActivating)
    new_win.show()

app = None

class MadnessAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(MadnessAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values.lower() == 'true':
            setattr(namespace, self.dest, True)
        elif values.lower() == 'false':
            setattr(namespace, self.dest, False)
        else:
            try:
                val = int(values)
            except ValueError:
                raise argparse.ArgumentTypeError(f"Invalid value '{values}' for --madness")
            if val < 0:
                raise argparse.ArgumentTypeError(f"Invalid value '{values}' for --madness")
            setattr(namespace, self.dest, val)

if __name__ == "__main__":
    # print pid
    print("Loading...")
    print("kill -9 " + str(os.getpid()))

    # parse madness flag
    parser = argparse.ArgumentParser()
    parser.add_argument('--madness', action=MadnessAction, help='Enable madness (integer or boolean)')

    args = parser.parse_args()
    #print(args.madness)

    new_progress_bar_interval = 2000
    if args.madness is not None:
        if type(args.madness) == bool:
            if args.madness:
                new_progress_bar_interval = 500
        else:
            new_progress_bar_interval = args.madness

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    create_moving_progress_bar()
    timer = QTimer()
    timer.timeout.connect(create_moving_progress_bar)
    timer.setInterval(new_progress_bar_interval)
    timer.start()

    signal.signal(signal.SIGINT, lambda *args: app.quit())

    sys.exit(app.exec())
