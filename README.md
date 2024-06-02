# To-Do List Application with Pomodoro Timer

A feature-rich to-do list application built using Python and Tkinter. This application allows you to manage your tasks efficiently with additional functionalities like a customizable Pomodoro timer.

## Features

- **Advanced GUI**: 
  - Black background with neon green theme for text and accents.
  - Custom fonts for a sleek look.

- **Task Management**: 
  - Add, delete, and mark tasks as complete.
  - Create nested subtasks indefinitely.
  - Multiple task lists with tabbed navigation.

- **Pomodoro Timer**: 
  - Customizable work and break intervals.
  - Alarm sound at the end of each interval.

- **Tab Management**:
  - Add, rename, and delete task lists.
  - Confirmation dialog for deleting lists.



## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/todo-list-app.git
    cd todo-list-app
    ```

2. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the application**:
    ```sh
    python main.py
    ```

## Usage

- **Adding Tasks**: Type in the task entry box and click 'Add Task'.
- **Adding Subtasks**: Click 'Add Subtask' next to the main task.
- **Completing Tasks**: Check the checkbox next to a task to mark it as complete.
- **Deleting Tasks**: Click 'Delete' next to a task.
- **Managing Lists**: Use the '+' tab to add new lists. Right-click a tab to rename or delete it.
- **Customizing Pomodoro Timer**: Click 'Customize Timer' to set custom work and break intervals.

## File Structure

```plaintext
todo-list-app/
│
├── main.py             # Main application code
├── tasks.json          # File to save tasks data
├── requirements.txt    # List of dependencies
├── README.md           # This readme file
└── assets/             # Directory for assets like screenshots
