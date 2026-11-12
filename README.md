<div align="center">🎓 AI Course Builder with Adaptive Learning Intelligence
Build personalized learning paths. Track concept mastery. Revise at the right time.
<p>
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" alt="React 19" />
  <img src="https://img.shields.io/badge/Python-Flask-3776AB?logo=python&logoColor=white" alt="Python Flask" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/AI-Google%20Gemini-8E75B2?logo=googlegemini&logoColor=white" alt="Google Gemini" />
  <img src="https://img.shields.io/badge/Build-Vite-646CFF?logo=vite&logoColor=white" alt="Vite" />
</p></div>📌 Table of Contents
- 📖 Overview
- ✨ Key Features
- 🧠 Adaptive Learning Modules
  - 1. AI Knowledge Dependency Graph (AKDG)
  - 2. Learner Digital Twin (LDT)
  - 3. Adaptive Memory Retention Engine (AMRE)
  - 4. Adaptive Revision Quizzes
- 🏗️ System Architecture
- 🛠️ Technology Stack
- ⚙️ Local Setup
- 🚀 Typical Application Workflow
- 🧪 Testing and Evaluation
- ⚠️ Current Limitations
- 🔮 Future Scope
- 📚 Project Report
📖 Overview
AI Course Builder with Adaptive Learning Intelligence is a web application that generates structured courses from a learner-provided topic, difficulty level, and duration. It connects AI-generated learning content with concept-level learner modelling and retention-based revision.

The application generates course syllabi, lessons, quizzes, revision quizzes, coding challenges, and knowledge graphs using Google Gemini. It also retrieves learning videos through the YouTube Data API v3.
✨ Key Features
Feature	Description
🔐 User Authentication	Registration, login, JWT-based authentication, token validation, and session restoration.
📚 AI Course Generation	Generates a multi-week course syllabus based on the selected topic, difficulty, and duration.
📝 Lesson Delivery	Presents generated lessons, summaries, and associated learning resources.
▶️ YouTube Recommendations	Retrieves up to three learning videos for each lesson using the YouTube Data API v3.
❓ Lesson Quizzes	Generates multiple-choice questions, evaluates submitted answers, and records concept-level performance.
💻 Coding Challenges	Generates coding challenges for courses identified as programming-related. The current implementation does not execute or automatically grade submitted code.
📈 Progress Tracking	Records lesson completion, quiz scores, and course progress.
🕸️ AI Knowledge Dependency Graph (AKDG)	Extracts course concepts and records relationships between them.
🧑‍🎓 Learner Digital Twin (LDT)	Maintains learner information such as concept-level strengths and weaknesses, quiz accuracy, learning speed, and difficulty tier using recorded learning evidence.
🧠 Adaptive Memory Retention Engine (AMRE)	Maintains a stability value for each concept, updates it using performance-based multipliers, and calculates when a concept is due for review.
🔄 Adaptive Revision Quizzes	Generates course-level revision quizzes for due concepts and adjusts each concept's question difficulty according to the learner's most recent accuracy.
🗂️ Revision History	Stores revision attempts and selected answers so previous attempts can be reviewed.


🧠 Adaptive Learning Modules
1. AI Knowledge Dependency Graph (AKDG)
AKDG represents concepts in a course as knowledge nodes and connects them through the following relationship types:
- prerequisite
- builds_on
- related_to
The graph is generated from the course structure and provides the concept references used by the learner-modelling and revision components.
Note: The relationships are advisory. They do not lock later lessons or automatically reorder the syllabus.

2. Learner Digital Twin (LDT)
LDT maintains a rule-based representation of learner performance. It uses quiz and concept-level learning evidence to track strengths, weaknesses, accuracy, learning speed, and a difficulty tier.

The project uses these accuracy bands:
Accuracy	Classification
80% or above	Strength
Below 60%	Weakness
60% to below 80%	Neither strength nor weakness


Note: LDT is a rule-based learner model. Its validity against real learning outcomes has not been established through a user study.

3. Adaptive Memory Retention Engine (AMRE)
AMRE stores a stability value for each concept and uses it to calculate the next review time.
Mechanism	Project rule
Initial stability	1, 2, or 3 days
Performance-based multipliers	0.5, 1.2, or 1.5
Stability range	1 to 30 days


Note: These values are design choices specific to this project and have not been calibrated using learner-study data.

4. Adaptive Revision Quizzes
When concepts become due for review, the application can generate a revision quiz for the relevant course. The quiz covers the due concepts and adjusts each concept's difficulty by one level according to the learner's most recent concept-level accuracy.
🏗️ System Architecture
The application uses a React single-page frontend, a Flask API Gateway, and five Flask services. The services use a shared PostgreSQL database through SQLAlchemy.

The frontend communicates with the backend through the API Gateway. The AI Service handles prompt construction, Gemini requests, development-mode generators, and response validation. The AI Service is not directly exposed through the Gateway.
Service Overview
Component	Port	Responsibility
🖥️ Frontend	5173	React user interface
🌐 API Gateway	5000	Entry point for frontend requests and request routing
🔐 Auth Service	5001	Registration, login, profile endpoints, password hashing, and JWT handling
📚 Course Service	5002	Course generation orchestration, course and lesson persistence, and AKDG pipeline
🤖 AI Service	5003	AI prompts, Gemini calls, development generators, and response validation
📝 Lesson Service	5004	Lesson operations, YouTube search, quizzes, revision quizzes, coding challenges, and evaluation
📊 Progress Service	5005	Progress, concept history, LDT, AMRE, and due-concept queries
🐘 PostgreSQL	—	Shared relational database


The database design documented in the project dissertation contains 15 tables.
🛠️ Technology Stack
Layer	Technology
Frontend	React 19, JavaScript
Build Tool	Vite
Routing	React Router DOM
Frontend Styling	Custom CSS
Frontend HTTP Communication	Browser Fetch API
Backend	Python, Flask
Architecture	Flask API Gateway and five Flask services
Database	PostgreSQL
ORM	SQLAlchemy
Authentication	Flask-JWT-Extended
Password Hashing	Werkzeug security
Generative AI SDK	google-genai
Generative AI Model	gemini-3.5-flash
Video Search	YouTube Data API v3
Backend Test Runner	pytest


⚙️ Local Setup
📋 Prerequisites
The project dissertation lists the following requirements:
- PostgreSQL 14 or higher
- Python 3.10–3.14
- Node.js 18 or higher
- A configured backend environment file
1. Configure Environment Variables
Create or configure backend/.env with the variables below. Use your own local values.
Variable	Purpose
DATABASE_URL	PostgreSQL connection URI
JWT_SECRET_KEY	Secret used to sign and verify JWTs
GEMINI_API_KEY	Google Gemini API key
AI_MODE	gemini for Gemini API calls or development for local mock generators
YOUTUBE_API_KEY	API key for YouTube Data API v3 searches


[!IMPORTANT]
Never commit API keys, database passwords, JWT secrets, or other sensitive values to GitHub.

2. Install Backend Dependencies
Open PowerShell in the project root and run:
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt
3. Initialize the Database Schema
Run this command once from the backend directory, with the backend environment activated and database configuration available:
python -m shared.database.init_database
4. Start the Backend Services
Start each service in a separate terminal. In each backend terminal, change to the backend directory and activate the virtual environment before running its command.

Auth Service — Port 5001
python -m services.auth_service.app
Course Service — Port 5002
python -m services.course_service.app
AI Service — Port 5003
python -m services.ai_service.app
Lesson Service — Port 5004
python -m services.lesson_service.app
Progress Service — Port 5005
python -m services.progress_service.app
API Gateway — Port 5000

Start the API Gateway in another backend terminal:
python -m api_gateway.app
5. Install and Start the Frontend
Open another terminal:
cd frontend

# Install frontend dependencies
npm install

# Start the Vite development server
npm run dev
Open the frontend in your browser:

http://localhost:5173

The frontend sends backend requests to the API Gateway at http://127.0.0.1:5000.
🚀 Typical Application Workflow
1. 🔐 Register or sign in.
2. 📚 Open Create Course.
3. ✍️ Enter a topic, select a difficulty level, and choose a course duration.
4. ⚙️ Generate the course.
5. 📖 Open the generated course and study its lessons.
6. ▶️ View the recommended learning videos for a lesson.
7. ❓ Generate and submit a lesson quiz.
8. ✅ Complete lessons and review progress on the dashboard.
9. 🔄 Open Revision Quizzes to see concepts due for review.
10. 📊 Start a revision quiz for a course and review the recorded attempt.
🧪 Testing and Evaluation
The project dissertation documents several forms of evidence, including manual functional checks, API checks, database testing, source-code/commit analysis, screenshots, and analytical verification of LDT and AMRE rules.
- The report records one automated database test for database connectivity and user CRUD operations.
- Dedicated automated unit tests for AMRE, LDT, and validators were not confirmed in the report.
- Performance, security, and usability testing were not documented as formally completed.
Evaluation note: The dissertation does not report a user study, a formal evaluation of the factual accuracy of AI-generated content, or performance benchmarks. Therefore, the project does not claim measured improvements in learning outcomes, reliability, or performance.

⚠️ Current Limitations
- Coding challenges display problem statements but do not execute or automatically grade code.
- AKDG relationships are advisory and do not lock or reorder lessons.
- The AI Doubt Solver is not implemented.
- The Settings page is a placeholder; profile endpoints exist in the backend but are not connected to the page.
- AI-generated content and knowledge-graph quality depend on the underlying model and validation.
- Gemini and YouTube functionality depends on external API availability and quotas.
- The system uses a shared database across services.
- The dissertation identifies limited testing evidence and no formal performance, security, or usability assessment.
🔮 Future Scope
The following enhancements are identified as future work in the project dissertation. They are not presented as implemented features.
- 💬 AI Doubt Solver within the lesson view.
- 🧑‍💻 Code-execution sandbox and automated judging for coding challenges.
- 🕸️ Interactive knowledge-graph visualization.
- ⚙️ Settings page integration with the profile API.
- 🔔 Revision reminders through email or push notifications.
- 👥 Role-based access, social login, and email password reset.
- 📘 Richer lesson content and user editing/reordering of the syllabus.
- 📈 Further evaluation of learning outcomes, AI content quality, accessibility, scalability, reliability, security, and deployment.
📚 Project Report
The project dissertation contains the detailed literature survey, requirements, architecture, database design, methodology, implementation, testing evidence, results, limitations, and future work.