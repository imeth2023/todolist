
# Todo App

This is a simple Todo application built using Python, Flask, and SQLite. The application allows users to sign up, log in, add tasks, view tasks, mark tasks as completed, move tasks back to the todo list, and delete tasks. The data is stored in a SQLite database, and the front-end is rendered using the Jinja2 template engine. The application uses the Fetch API for client-server communication.

## Features

- User Authentication (Sign up, Log in, Log out)
- Add tasks with due dates and priority
- Mark tasks as completed
- Move completed tasks back to the todo list by drag and dropping
- Sort and filter tasks by due date and priority
- Error handling for login and signup

## Requirements

- Python 3.x
- Flask
- SQLite3

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/imeth2023/todolist
    
    ```

2. (Optional) Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Initialize the database:

    ```bash
    python db_create.py
    ```


## Usage

1. Start the  server:

    ```bash
    flask run
    ```

2. Open [http://localhost:5000](http://localhost:5000) in your web browser.



