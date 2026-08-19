from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Note:
    id: Optional[int] = None
    title: str = "Untitled Voice Note"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    duration: str = "00:00"
    audio_path: Optional[str] = None
    category: str = "General"


@dataclass
class Transcript:
    id: Optional[int] = None
    note_id: Optional[int] = None
    raw_text: str = ""
    cleaned_text: str = ""
    language: str = "en"


@dataclass
class AISummary:
    id: Optional[int] = None
    note_id: Optional[int] = None
    summary: str = ""
    key_points: List[str] = field(default_factory=list)
    sentiment: str = "Neutral"
    main_topics: List[str] = field(default_factory=list)


@dataclass
class Task:
    id: Optional[int] = None
    note_id: Optional[int] = None
    title: str = ""
    description: str = ""
    priority: str = "Medium"  # High, Medium, Low
    assignee: str = "Unassigned"
    due_date: str = "TBD"
    status: str = "Pending"  # Pending, In Progress, Completed


@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    full_name: str = "VoiceNote User"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    avatar_url: Optional[str] = None

