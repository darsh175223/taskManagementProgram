import tkinter as tk
from tkinter import ttk, font, messagebox
from datetime import datetime
import json
import os
import time
import threading
import winsound

# Constants
BG_COLOR = "#000000"
TEXT_COLOR = "#00FF00"
ACCENT_COLOR = "#00FF00"
FONT_NAME = "Helvetica"
FONT_SIZE = 12
TASK_FILE = "tasks.json"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


# Helper functions
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r') as file:
            return json.load(file)
    return {}


def save_tasks(tasks):
    with open(TASK_FILE, 'w') as file:
        json.dump(tasks, file)


# Task Manager class
class TaskManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(bg=BG_COLOR)
        self.tasks = load_tasks()
        self.current_list = 'Default'
        self.task_lists = {self.current_list: self.tasks}

        # Pomodoro Timer Variables
        self.work_minutes = tk.IntVar(value=25)
        self.break_minutes = tk.IntVar(value=5)

        # Custom font
        self.custom_font = font.Font(family=FONT_NAME, size=FONT_SIZE)

        # Main frame
        self.main_frame = tk.Frame(self, bg=BG_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

        # Add default tab
        self.add_tab(self.current_list)

        # Pomodoro timer
        self.timer_running = False
        self.timer_label = tk.Label(self, text="00:00", font=self.custom_font, bg=BG_COLOR, fg=ACCENT_COLOR)
        self.timer_label.pack(side=tk.BOTTOM, pady=10)

        pomodoro_frame = tk.Frame(self, bg=BG_COLOR)
        pomodoro_frame.pack(side=tk.BOTTOM, pady=10)

        self.pomodoro_button = tk.Button(pomodoro_frame, text="Start Pomodoro", command=self.start_pomodoro,
                                         font=self.custom_font, bg=ACCENT_COLOR)
        self.pomodoro_button.pack(side=tk.LEFT, padx=5)

        self.customize_button = tk.Button(pomodoro_frame, text="Customize Timer", command=self.customize_timer,
                                          font=self.custom_font, bg=ACCENT_COLOR)
        self.customize_button.pack(side=tk.LEFT, padx=5)

        # Add '+' tab
        self.add_plus_tab()

    def add_tab(self, list_name):
        frame = tk.Frame(self.notebook, bg=BG_COLOR)
        tab_name = self.create_unique_list_name(list_name)

        if len(self.notebook.tabs()) > 1:
            self.notebook.insert(len(self.notebook.tabs()) - 1, frame, text=tab_name)
        else:
            self.notebook.add(frame, text=tab_name)

        # Entry for tasks
        entry_frame = tk.Frame(frame, bg=BG_COLOR)
        entry_frame.pack(pady=10)

        task_entry = tk.Entry(entry_frame, font=self.custom_font, bg=BG_COLOR, fg=TEXT_COLOR,
                              insertbackground=TEXT_COLOR)
        task_entry.pack(side=tk.LEFT, padx=(0, 10))

        add_task_button = tk.Button(entry_frame, text="Add Task", command=lambda: self.add_task(task_entry, frame),
                                    font=self.custom_font, bg=ACCENT_COLOR)
        add_task_button.pack(side=tk.LEFT)

        task_frame = tk.Frame(frame, bg=BG_COLOR)
        task_frame.pack(fill=tk.BOTH, expand=True)

        self.task_lists[tab_name] = {"task_entry": task_entry, "task_frame": task_frame, "tasks": {}}
        self.display_tasks(tab_name)

    def add_plus_tab(self):
        frame = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(frame, text='+')
        self.notebook.tab(self.notebook.tabs()[-1], state="disabled")
        add_list_button = tk.Button(frame, text="Add New List", command=self.add_new_list, font=self.custom_font,
                                    bg=ACCENT_COLOR)
        add_list_button.pack(expand=True)

    def add_new_list(self):
        new_list_name = "List"
        self.add_tab(new_list_name)
        self.notebook.select(len(self.notebook.tabs()) - 2)

    def tab_changed(self, event):
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == '+':
            self.add_new_list()
        else:
            self.current_list = current_tab

    def create_unique_list_name(self, base_name):
        count = 1
        new_name = f"{base_name} {count}"
        while new_name in self.task_lists:
            count += 1
            new_name = f"{base_name} {count}"
        return new_name

    def add_task(self, task_entry, frame):
        task_text = task_entry.get().strip()
        if task_text:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            tasks = self.task_lists[current_tab]["tasks"]
            tasks[task_text] = {"completed": False, "subtasks": {}}
            self.save_and_refresh(current_tab)
            task_entry.delete(0, tk.END)

    def delete_task(self, task_text, list_name):
        tasks = self.task_lists[list_name]["tasks"]
        if task_text in tasks:
            del tasks[task_text]
            self.save_and_refresh(list_name)

    def mark_task_complete(self, task_text, list_name):
        tasks = self.task_lists[list_name]["tasks"]
        if task_text in tasks:
            tasks[task_text]["completed"] = not tasks[task_text]["completed"]
            self.save_and_refresh(list_name)

    def add_subtask(self, task_text, list_name, parent_task=None):
        def save_subtask():
            subtask_text = subtask_entry.get().strip()
            if subtask_text:
                tasks = self.task_lists[list_name]["tasks"]
                parent = tasks[task_text] if parent_task is None else parent_task["subtasks"]
                parent[subtask_text] = {"completed": False, "subtasks": {}}
                self.save_and_refresh(list_name)
                subtask_window.destroy()

        subtask_window = tk.Toplevel(self)
        subtask_window.title("Add Subtask")
        subtask_window.geometry("300x100")

        subtask_entry = tk.Entry(subtask_window, font=self.custom_font, bg=BG_COLOR, fg=TEXT_COLOR,
                                 insertbackground=TEXT_COLOR)
        subtask_entry.pack(pady=10)

        add_subtask_button = tk.Button(subtask_window, text="Add Subtask", command=save_subtask, font=self.custom_font,
                                       bg=ACCENT_COLOR)
        add_subtask_button.pack()

    def delete_subtask(self, task_text, subtask_text, list_name, parent_task=None):
        tasks = self.task_lists[list_name]["tasks"]
        parent = tasks[task_text] if parent_task is None else parent_task["subtasks"]
        if subtask_text in parent:
            del parent[subtask_text]
            self.save_and_refresh(list_name)

    def save_and_refresh(self, list_name):
        save_tasks(self.task_lists[list_name]["tasks"])
        self.display_tasks(list_name)

    def display_tasks(self, list_name):
        task_frame = self.task_lists[list_name]["task_frame"]
        for widget in task_frame.winfo_children():
            widget.destroy()

        tasks = self.task_lists[list_name]["tasks"]
        for task_text, task_data in tasks.items():
            self.display_task(task_frame, task_text, task_data, list_name, 0)

    def display_task(self, parent_frame, task_text, task_data, list_name, indent_level):
        indent = " " * (4 * indent_level)

        task_frame_inner = tk.Frame(parent_frame, bg=BG_COLOR)
        task_frame_inner.pack(fill=tk.X, pady=2)

        task_checkbox = tk.Checkbutton(task_frame_inner, text=indent + task_text,
                                       variable=tk.IntVar(value=task_data["completed"]),
                                       command=lambda t=task_text: self.mark_task_complete(t, list_name),
                                       font=self.custom_font,
                                       bg=BG_COLOR, fg=TEXT_COLOR, activebackground=BG_COLOR,
                                       activeforeground=TEXT_COLOR,
                                       selectcolor=BG_COLOR)
        task_checkbox.pack(side=tk.LEFT)

        subtask_button = tk.Button(task_frame_inner, text="Add Subtask",
                                   command=lambda t=task_text: self.add_subtask(t, list_name, task_data),
                                   font=self.custom_font, bg=ACCENT_COLOR)
        subtask_button.pack(side=tk.LEFT, padx=(10, 0))

        delete_button = tk.Button(task_frame_inner, text="Delete",
                                  command=lambda t=task_text: self.delete_task(t, list_name),
                                  font=self.custom_font, bg=ACCENT_COLOR)
        delete_button.pack(side=tk.LEFT, padx=(10, 0))

        subtask_frame = tk.Frame(parent_frame, bg=BG_COLOR, padx=20)
        subtask_frame.pack(fill=tk.X, pady=2)
        for subtask_text, subtask_data in task_data["subtasks"].items():
            self.display_task(subtask_frame, subtask_text, subtask_data, list_name, indent_level + 1)

    def mark_subtask_complete(self, task_text, subtask_text, list_name, parent_task):
        parent = self.task_lists[list_name]["tasks"][task_text] if parent_task is None else parent_task["subtasks"]
        if subtask_text in parent["subtasks"]:
            parent["subtasks"][subtask_text]["completed"] = not parent["subtasks"][subtask_text]["completed"]
            self.save_and_refresh(list_name)

    def start_pomodoro(self):
        if not self.timer_running:
            self.timer_running = True
            self.pomodoro_button.config(text="Stop Pomodoro", command=self.stop_pomodoro)
            self.run_pomodoro(self.work_minutes.get() * 60)

    def stop_pomodoro(self):
        self.timer_running = False
        self.pomodoro_button.config(text="Start Pomodoro", command=self.start_pomodoro)
        self.timer_label.config(text="00:00")

    def run_pomodoro(self, seconds):
        if self.timer_running:
            if seconds > 0:
                mins, secs = divmod(seconds, 60)
                time_format = '{:02d}:{:02d}'.format(mins, secs)
                self.timer_label.config(text=time_format)
                self.after(1000, self.run_pomodoro, seconds - 1)
            else:
                self.play_alarm()
                if seconds == self.work_minutes.get() * 60:
                    self.run_pomodoro(self.break_minutes.get() * 60)
                else:
                    self.stop_pomodoro()

    def play_alarm(self):
        winsound.Beep(440, 1000)  # 440 Hz for 1 second

    def customize_timer(self):
        def save_custom_time():
            work_time = work_time_entry.get().strip()
            break_time = break_time_entry.get().strip()
            if work_time.isdigit() and break_time.isdigit():
                self.work_minutes.set(int(work_time))
                self.break_minutes.set(int(break_time))
                custom_time_window.destroy()
            else:
                messagebox.showerror("Invalid Input", "Please enter valid integers for work and break times.")

        custom_time_window = tk.Toplevel(self)
        custom_time_window.title("Customize Timer")
        custom_time_window.geometry("400x200")

        tk.Label(custom_time_window, text="Work Time (minutes):", font=self.custom_font, bg=BG_COLOR,
                 fg=TEXT_COLOR).pack(pady=5)
        work_time_entry = tk.Entry(custom_time_window, font=self.custom_font, bg=BG_COLOR, fg=TEXT_COLOR,
                                   insertbackground=TEXT_COLOR)
        work_time_entry.insert(0, str(self.work_minutes.get()))
        work_time_entry.pack(pady=5)

        tk.Label(custom_time_window, text="Break Time (minutes):", font=self.custom_font, bg=BG_COLOR,
                 fg=TEXT_COLOR).pack(pady=5)
        break_time_entry = tk.Entry(custom_time_window, font=self.custom_font, bg=BG_COLOR, fg=TEXT_COLOR,
                                    insertbackground=TEXT_COLOR)
        break_time_entry.insert(0, str(self.break_minutes.get()))
        break_time_entry.pack(pady=5)

        save_button = tk.Button(custom_time_window, text="Save", command=save_custom_time, font=self.custom_font,
                                bg=ACCENT_COLOR)
        save_button.pack(pady=10)

    def rename_tab(self, list_name):
        def save_new_name():
            new_name = name_entry.get().strip()
            if new_name and new_name not in self.task_lists:
                self.task_lists[new_name] = self.task_lists.pop(list_name)
                tab_index = self.notebook.index(self.notebook.select())
                self.notebook.tab(tab_index, text=new_name)
                rename_window.destroy()
            else:
                messagebox.showerror("Invalid Name", "Please enter a valid, unique name.")

        rename_window = tk.Toplevel(self)
        rename_window.title("Rename Tab")
        rename_window.geometry("300x100")

        tk.Label(rename_window, text="New Name:", font=self.custom_font, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)
        name_entry = tk.Entry(rename_window, font=self.custom_font, bg=BG_COLOR, fg=TEXT_COLOR,
                              insertbackground=TEXT_COLOR)
        name_entry.pack(pady=5)

        save_button = tk.Button(rename_window, text="Save", command=save_new_name, font=self.custom_font,
                                bg=ACCENT_COLOR)
        save_button.pack(pady=10)

    def delete_tab(self, list_name):
        def confirm_delete():
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the list '{list_name}'?"):
                del self.task_lists[list_name]
                tab_index = self.notebook.index(self.notebook.select())
                self.notebook.forget(tab_index)
                confirm_window.destroy()

        confirm_window = tk.Toplevel(self)
        confirm_window.title("Confirm Delete")
        confirm_window.geometry("300x100")

        tk.Label(confirm_window, text=f"Delete the list '{list_name}'?", font=self.custom_font, bg=BG_COLOR,
                 fg=TEXT_COLOR).pack(pady=5)
        confirm_button = tk.Button(confirm_window, text="Delete", command=confirm_delete, font=self.custom_font,
                                   bg=ACCENT_COLOR)
        confirm_button.pack(pady=10)


if __name__ == "__main__":
    app = TaskManager()
    app.mainloop()
