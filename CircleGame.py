import ctypes

# Setting DPI Awareness (Windows 10 and 8)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except AttributeError:
    # Fallback for older Windows versions
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass  # If the OS doesn't support DPI awareness, there's nothing we can do


import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import time
from math import pi, atan2

# DPI AWARENESS
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except AttributeError:
    pass

# Get system DPI


def get_system_dpi():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


# Calculate scaling factor
screen_width, screen_height = get_system_dpi()
scaling_factor = screen_height / 1080  # Assuming 1080p is the base resolution


def scale(value):
    return int(value * scaling_factor)


class CircleGame:

    def __init__(self, master):
        self.master = master
        self.master.title("Circle Game")

        canvas_width = scale(300)
        canvas_height = scale(300)

        self.canvas = tk.Canvas(
            master, width=canvas_width, height=canvas_height)
        self.canvas.pack()

        # Define circle center and radius here
        self.circle_center = canvas_width // 2
        self.circle_radius = scale(100)

        self.segments = [True, True, True]  # True for white, False for black

        self.draw_circle()

        self.player_count = simpledialog.askinteger(
            "Players", "Enter the number of players:")
        self.current_player = 1
        self.scores = [0] * self.player_count
        self.start_time = time.time()
        self.game_duration = 30  # playtime in seconds
        self.clicks_this_turn = 0
        self.clicks_needed = 0

        self.status_label = tk.Label(master, text="", font=("Helvetica", 12))
        self.status_label.pack()

        self.canvas.bind("<Button-1>", self.click_segment)
        self.next_turn()
        self.update_time()

    def draw_circle(self):
        self.canvas.delete("all")
        angles = [(0, 120), (120, 240), (240, 360)]  # circle segments

        for i, (start, end) in enumerate(angles):
            self.draw_segment(start, end, self.segments[i])
        self.canvas.update()

    def draw_segment(self, start, end, is_white):
        color = "white" if is_white else "black"
        self.canvas.create_arc(self.circle_center - self.circle_radius,
                               self.circle_center - self.circle_radius,
                               self.circle_center + self.circle_radius,
                               self.circle_center + self.circle_radius,
                               start=start, extent=end - start, fill=color, tags="segment")

    def click_segment(self, event):
        if self.clicks_this_turn < self.clicks_needed:
            x, y = event.x - self.circle_center, event.y - self.circle_center
            angle = (180 / pi) * atan2(y, x)
            if angle < 0:
                angle += 360  # Correct for some weird negative coordinate stuff
            segment_index = self.determine_segment(angle)
            self.segments[segment_index] = not self.segments[segment_index]
            self.draw_circle()
            self.clicks_this_turn += 1
            self.update_status()

            if self.clicks_this_turn == self.clicks_needed:
                if all(not seg for seg in self.segments):  # All segments are black
                    self.scores[self.current_player - 1] += 1
                    self.segments = [True, True, True]  # Reset to white
                    self.draw_circle()

                self.current_player = (self.current_player %
                                       self.player_count) + 1
                self.clicks_this_turn = 0
                self.next_turn()

    def determine_segment(self, angle):
        if 0 <= angle < 120:
            return 2
        elif 120 <= angle < 240:
            return 1
        else:
            return 0

    def next_turn(self):
        if time.time() - self.start_time > self.game_duration:
            self.end_game()
            return

        self.clicks_needed = random.randint(1, 3)
        self.update_status()

    def update_status(self):
        elapsed_time = time.time() - self.start_time
        remaining_time = self.game_duration - elapsed_time
        minutes, seconds = divmod(int(remaining_time), 60)
        time_str = f"Time: {minutes:02d}:{seconds:02d}"

        top_player = max(range(len(self.scores)),
                         key=self.scores.__getitem__) + 1

        top_score = max(self.scores)
        self.status_label.config(text=f"{time_str}\nPlayer {self.current_player}'s turn. Clicks left: {
                                 self.clicks_needed - self.clicks_this_turn}\nTop Player: Player {top_player} with {top_score} points")

    def update_time(self):
        self.update_status()
        self.master.after(1000, self.update_time)  # Update every second

    def end_game(self):
        end_message = "Game over!\nScores:\n" + \
            "\n".join(f"Player {i+1}: {score}" for i,
                      score in enumerate(self.scores))
        messagebox.showinfo("Game Over", end_message)
        self.master.quit()


root = tk.Tk()
game = CircleGame(root)
root.mainloop()
