# Prerequisites for CSV Data Management System

## System Requirements

### Operating System:
- `Linux/Unix` environment (recommended for cron jobs)
- `Windows/macOS` (supported but may require different task scheduling)

---

## Software Dependencies

### Python Environment:
- `Python 3.8` or higher
- `pip` package manager

### Database:
- `PostgreSQL 12.0` or higher
- `psycopg2-binary` for PostgreSQL connection

### Core Framework:
- `Django 4.2` or higher
- `Django REST framework` (if API endpoints are needed)

---

## Python Packages

### Required Packages:
- `Django (4.2)`: The core framework for building the web application, handling routing, views, and models.
- `psycopg2-binary (2.9.9)`: PostgreSQL adapter for Python, facilitating efficient database connectivity and operations.
- `django-tailwind (3.8.0)`: Integrates the Tailwind CSS framework for modern and utility-first styling in the project.
- `django-browser-reload (1.12.1)`: Provides automatic browser reloading to enhance the development experience.
- `django-compressor (4.4)`: Optimizes and compresses static files such as CSS and JavaScript for faster page load times.
- `django-htmx (1.17.2)`: Enables dynamic HTML updates without full-page reloads, enhancing the user experience.
- `pandas (2.1.4)`: A powerful library for data manipulation, particularly useful for processing and analyzing CSV files.
- `django-rest-framework (0.1.0)`: A toolkit for building and managing Web APIs, allowing interaction with external systems or clients.
- `plotly`: A library for creating interactive and visually appealing data visualizations like charts and graphs.
- `django-unfold`: A modern theme for Django's admin interface, improving aesthetics and usability.
- `django-cron`: Facilitates the scheduling and execution of periodic tasks, such as hourly data exports.


---

## Development Tools

### Version Control:
- `Git 2.0` or higher

### IDE/Code Editor:
- Any Python-compatible IDE (`VSCode`, `PyCharm` recommended)
- Database management tool (e.g., `pgAdmin`, `DBeaver`)

---

## System Access

### Permissions:
- Database creation/modification privileges
- File system read/write permissions
- Cron job creation capabilities (sudo access might be required)

---

## Knowledge Requirements

### Technical Skills Needed:
- Basic Python programming
- Django framework fundamentals
- SQL and PostgreSQL basics
- Understanding of CSV file structure
- Basic Linux commands (for cron setup)
- Database design principles

---
