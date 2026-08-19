# 🗄️ PostgreSQL Database Setup Guide — VoiceNote

This document provides complete instructions for configuring, initializing, and managing the **strictly PostgreSQL** persistence layer for the **VoiceNote** desktop application.

---

## 📌 Architecture Overview

VoiceNote uses a dedicated **PostgreSQL** relational database engine via `psycopg2`.

- **Engine**: Locked to `postgres` (`DB_ENGINE = "postgres"` in `voicenote/config.py`).
- **Auto-Provisioning**: Programmatically checks for and creates the target `voicenote` database on startup if missing.
- **Relational Integrity**: Foreign keys with `ON DELETE CASCADE` from `notes` to `transcripts`, `ai_summaries`, and `tasks`.

---

## 🛠️ Prerequisites

1. **PostgreSQL Server** (v14 or higher) installed and running locally on port `5432`.
2. **pgAdmin 4** (Optional, recommended for visual database management).
3. **Python 3.10+** with `psycopg2-binary` installed (`pip install psycopg2-binary`).

---

## ⚙️ 1. Environment Configuration (`.env`)

Copy `.env.example` to create `.env` in the root workspace directory:

```bash
cp .env.example .env
```

Update your `.env` file with your local PostgreSQL credentials:

```env
# PostgreSQL Database Configuration
DB_ENGINE=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=voicenote
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_actual_postgres_password
```

---

## 🗂️ 2. Database Schema

The database consists of 5 core relational tables:

### 1. `users` Table (Authentication & Profiles)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | User identifier |
| `username` | VARCHAR(100) | UNIQUE, NOT NULL | Login username |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Account email |
| `password_hash` | VARCHAR(255) | NOT NULL | SHA-256 hashed password |
| `full_name` | VARCHAR(255) | DEFAULT 'VoiceNote User' | Display name |
| `created_at` | VARCHAR(100) | NOT NULL | Timestamp |
| `avatar_url` | TEXT | NULL | Profile image link |

### 2. `notes` Table (Voice Note Metadata)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | Note identifier |
| `title` | VARCHAR(255) | NOT NULL | Note title |
| `created_at` | VARCHAR(100) | NOT NULL | Creation timestamp |
| `duration` | VARCHAR(50) | DEFAULT '00:00' | Audio length |
| `audio_path` | TEXT | NULL | Local audio file location |
| `category` | VARCHAR(100) | DEFAULT 'General' | Tag / category |

### 3. `transcripts` Table (STT Output)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | Transcript ID |
| `note_id` | INTEGER | FK -> notes(id) ON DELETE CASCADE | Associated note |
| `raw_text` | TEXT | NOT NULL | Raw Whisper transcript |
| `cleaned_text` | TEXT | NULL | Post-processed transcript |
| `language` | VARCHAR(20) | DEFAULT 'en' | Spoken language |

### 4. `ai_summaries` Table (LLM Intelligence)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | Summary ID |
| `note_id` | INTEGER | FK -> notes(id) ON DELETE CASCADE | Associated note |
| `summary` | TEXT | NOT NULL | Executive summary |
| `key_points` | TEXT | NULL | JSON array of key takeaways |
| `sentiment` | VARCHAR(50) | DEFAULT 'Neutral' | Tone analysis |
| `main_topics` | TEXT | NULL | JSON array of topics |

### 5. `tasks` Table (Action Items)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | Task ID |
| `note_id` | INTEGER | FK -> notes(id) ON DELETE CASCADE | Origin note |
| `title` | VARCHAR(255) | NOT NULL | Action item title |
| `description` | TEXT | NULL | Task details |
| `priority` | VARCHAR(50) | DEFAULT 'Medium' | High, Medium, Low |
| `assignee` | VARCHAR(100) | DEFAULT 'Unassigned' | Owner |
| `due_date` | VARCHAR(100) | DEFAULT 'TBD' | Target date |
| `status` | VARCHAR(50) | DEFAULT 'Pending' | Pending, Completed |

---

## 🚀 3. Initializing & Seeding the Database

Run the database setup script to auto-create the database, create tables, and seed initial sample data:

```powershell
.\.venv\Scripts\python.exe -m voicenote.db.database
```

**Expected Output:**
```text
Initializing VoiceNote PostgreSQL Database...
INFO:DatabaseManager:Default demo user ('admin' / 'admin123') created successfully.
PostgreSQL Database initialized successfully!
Total Users: 1
Total Notes: 3
Total Tasks: 3
```

---

## 🖥️ 4. Setting Up pgAdmin 4 (GUI Setup)

To visually view and query your PostgreSQL database in **pgAdmin 4**:

1. **Connect to PostgreSQL Server**:
   - Open **pgAdmin 4**.
   - Click **Add New Server** under *Quick Links*.
   - **General Tab**: Name: `VoiceNote Local`
   - **Connection Tab**:
     - Host: `localhost`
     - Port: `5432`
     - Database: `postgres`
     - Username: `postgres`
     - Password: *(Your PostgreSQL superuser password)*
     - Check **Save Password?**.
   - Click **Save**.

2. **View `voicenote` Database**:
   - In pgAdmin left panel: `Servers` $\rightarrow$ `VoiceNote Local` $\rightarrow$ `Databases` $\rightarrow$ `voicenote`.
   - Expand `Schemas` $\rightarrow$ `public` $\rightarrow$ `Tables`.
   - Right-click any table (e.g. `users` or `notes`) $\rightarrow$ **View/Edit Data** $\rightarrow$ **All Rows**.

---

## 🧪 5. Running Database Unit Tests

To verify CRUD operations and authentication routines:

```powershell
.\.venv\Scripts\python.exe -m unittest tests/test_db.py
```

All 7 unit tests should return `OK`.
