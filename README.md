 📘 Course Enrollment Platform API

 📌 Project Description

This project is a secure RESTful API built with FastAPI for managing a course enrollment system. It supports authentication, role-based access control, and database-backed operations using PostgreSQL.
 🚀 Features

 👤 User Management

* User registration
* User login with JWT authentication
* User profile access
* Role-based access (student / admin)

 📚 Course Management

* View all active courses (public)
* View single course (public)
* Admin can:

  * Create courses
  * Update courses
  * Activate / deactivate courses
  * Delete courses

🎓 Enrollment System

* Students can enroll in courses
* Students can deregister from courses
* Prevent duplicate enrollment
* Prevent enrollment if course is full
* Prevent enrollment if course is inactive

-🛠 Admin Features

* View all enrollments
* View enrollments per course
* Remove students from courses

 🔐 Authentication & Authorization

* JWT-based authentication
* Password hashing using bcrypt
* Role-Based Access Control (RBAC)

| Action             | Student | Admin |
| ------------------ | ------- | ----- |
| View courses       | ✅       | ✅     |
| Enroll in course   | ✅       | ❌     |
| Create course      | ❌       | ✅     |
| Manage enrollments | ❌       | ✅     |

🗄 Database

* PostgreSQL database
* SQLAlchemy ORM
* Alembic migrations
* Relationships:

  * User → Enrollment
  * Course → Enrollment


