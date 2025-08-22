# 📚 My Development Stack Templates

Welcome! This repository is a personal collection of pre-configured, Docker-based development environments ("stacks") that I use for various projects. The goal is to have ready-to-use templates to kickstart new projects quickly without setting everything up from scratch.



---
## 📂 How to Use

1.  Browse the list of available stacks in the table below.
2.  Click on the stack name to navigate to its directory.
3.  Follow the instructions in the `README.md` file *inside that specific directory* to get started.

---
## ✨ Available Stacks

Here are the currently available stacks in this repository:

| Stack | Description | Key Services |
| :--- | :--- | :--- |
| **[Postgres + MinIO](./postgres-minio/)** | A simple stack with a PostgreSQL database and MinIO for S3-compatible object storage. | `Airflow`, `Spark`, `PostgreSQL`, `MinIO` |
| **[MySQL + phpMyAdmin](./mysql-phpmyadmin/)** | A basic MySQL stack with phpMyAdmin for easy web-based database administration. | `Airflow`, `Spark`, `MySQL`, `phpMyAdmin` |

---
## 💡 Contributing a New Stack

To add a new template to this collection, follow these steps:

1.  Create a new directory with a descriptive name (e.g., `redis-cache-stack`).
2.  Add all necessary files (`docker-compose.yml`, `.env.example`, etc.).
3.  **Crucially, create a detailed `README.md` inside the new directory** explaining what the stack is for and how to use it.
4.  Update the table in this main `README.md` file to include a link to your new stack.

---
## 📄 License

This collection is for personal use and is licensed under the MIT License.
