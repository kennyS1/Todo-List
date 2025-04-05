# Todo List Application

## Project Overview

This is a simple Todo List application built with **FastAPI** for the backend and **React** for the frontend. The app allows users to manage tasks by adding, marking as completed, and deleting items. It also includes basic user authentication via JWT (JSON Web Tokens).

## Features

- **User Authentication**: Secure login and registration using JWT tokens.
- **Task Management**: Add, delete, and mark tasks as completed.
- **Real-time Updates**: The Todo list dynamically updates when tasks are added, completed, or deleted.
- **Responsive Design**: The user interface is responsive and works across various devices.

## Technologies Used

- **Backend**: FastAPI
- **Frontend**: React
- **Database**: SQLite (or any other database you're using)
- **Authentication**: JWT (JSON Web Tokens)
- **Styling**: CSS/Styled-components (or any other styling method you're using)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/kennyS1/Todo-List.git
cd Todo-List
```

### 1. Install dependencies
#### For the backend:
#### 1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
.\venv\Scripts\activate  # On Windows
```
#### 2. create the database: execute the todo_db.sql

#### 3. Install the required packages:
```bash
pip install -r requirements.txt
```

#### For the frontend:
#### 1. Navigate to the frontend directory:
```bash
cd frontend
```
#### 2. Install the frontend dependencies:
```bash
npm install
```
### 3. Run the project
#### ~ Start the FastAPI backend server:
```bash
py main.py
```
#### ~ Start the React frontend:
```bash
npm run dev
```



### 4. Access the application
#### The backend will run at http://localhost:8000
#### The frontend will run at http://localhost:3000

### 5. How to Use
#### Add Task: Enter a task description in the input field and click "Add".
#### Complete Task: Click the "Complete" button next to a task to mark it as completed.
#### Delete Task: Click the "Delete" button next to a task to remove it from the list.



