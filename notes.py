"""
PKMS Note Management System
Store, link, and manage notes/documents
"""

import json
import uuid
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Storage setup
DATA_DIR = Path(os.environ.get("PKMS_DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_DIR = DATA_DIR / "notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)
NOTES_INDEX = DATA_DIR / "notes_index.json"

@dataclass
class Note:
    id: str
    title: str
    content: str
    tags: List[str]
    created: str
    modified: str
    linked_tasks: List[str]  # Task IDs this note is linked to

# ============ INTERNAL HELPERS ============

def _gen_id() -> str:
    """Generate short ID"""
    return uuid.uuid4().hex[:8]

def _load_index() -> List[Note]:
    """Load notes index from JSON"""
    if not NOTES_INDEX.exists():
        return []
    try:
        raw = json.loads(NOTES_INDEX.read_text(encoding="utf-8"))
        return [Note(**n) for n in raw]
    except:
        return []

def _save_index(notes: List[Note]) -> None:
    """Save notes index to JSON"""
    NOTES_INDEX.write_text(
        json.dumps([asdict(n) for n in notes], indent=2),
        encoding="utf-8"
    )

def _match_by_prefix(notes: List[Note], prefix: str) -> Optional[Note]:
    """Find note by ID prefix"""
    prefix = prefix.strip().lower()
    matches = [n for n in notes if n.id.lower().startswith(prefix)]
    return matches[0] if len(matches) == 1 else None

def _get_note_path(note_id: str) -> Path:
    """Get file path for note content"""
    return NOTES_DIR / f"{note_id}.md"

def _timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ============ PUBLIC API ============

def create_note(title: str, content: str = "", tags: List[str] = None) -> Note:
    """Create a new note"""
    note = Note(
        id=_gen_id(),
        title=title.strip(),
        content=content,
        tags=tags or [],
        created=_timestamp(),
        modified=_timestamp(),
        linked_tasks=[]
    )
    
    # Save content to file
    note_path = _get_note_path(note.id)
    note_path.write_text(content, encoding="utf-8")
    
    # Update index
    notes = _load_index()
    notes.append(note)
    _save_index(notes)
    
    return note

def get_note(note_id_prefix: str) -> Optional[Note]:
    """Get a note by ID prefix"""
    notes = _load_index()
    note = _match_by_prefix(notes, note_id_prefix)
    
    if note:
        # Load content from file
        note_path = _get_note_path(note.id)
        if note_path.exists():
            note.content = note_path.read_text(encoding="utf-8")
    
    return note

def list_notes() -> List[Note]:
    """List all notes (without content)"""
    return _load_index()

def update_note(note_id_prefix: str, title: str = None, content: str = None, tags: List[str] = None) -> Optional[Note]:
    """Update a note"""
    notes = _load_index()
    note = _match_by_prefix(notes, note_id_prefix)
    
    if not note:
        return None
    
    # Update fields
    if title is not None:
        note.title = title.strip()
    if content is not None:
        note.content = content
        # Save content to file
        note_path = _get_note_path(note.id)
        note_path.write_text(content, encoding="utf-8")
    if tags is not None:
        note.tags = tags
    
    note.modified = _timestamp()
    
    # Save index
    _save_index(notes)
    return note

def delete_note(note_id_prefix: str) -> bool:
    """Delete a note"""
    notes = _load_index()
    note = _match_by_prefix(notes, note_id_prefix)
    
    if not note:
        return False
    
    # Delete content file
    note_path = _get_note_path(note.id)
    if note_path.exists():
        note_path.unlink()
    
    # Remove from index
    notes = [n for n in notes if n.id != note.id]
    _save_index(notes)
    return True

def search_notes(query: str) -> List[Note]:
    """Search notes by title or content"""
    query = query.strip().lower()
    notes = _load_index()
    results = []
    
    for note in notes:
        # Search in title
        if query in note.title.lower():
            results.append(note)
            continue
        
        # Search in content
        note_path = _get_note_path(note.id)
        if note_path.exists():
            content = note_path.read_text(encoding="utf-8").lower()
            if query in content:
                note.content = note_path.read_text(encoding="utf-8")
                results.append(note)
    
    return results

def link_note_to_task(note_id_prefix: str, task_id: str) -> Optional[Note]:
    """Link a note to a task"""
    notes = _load_index()
    note = _match_by_prefix(notes, note_id_prefix)
    
    if not note:
        return None
    
    if task_id not in note.linked_tasks:
        note.linked_tasks.append(task_id)
        note.modified = _timestamp()
        _save_index(notes)
    
    return note

def unlink_note_from_task(note_id_prefix: str, task_id: str) -> Optional[Note]:
    """Unlink a note from a task"""
    notes = _load_index()
    note = _match_by_prefix(notes, note_id_prefix)
    
    if not note:
        return None
    
    if task_id in note.linked_tasks:
        note.linked_tasks.remove(task_id)
        note.modified = _timestamp()
        _save_index(notes)
    
    return note

def get_notes_for_task(task_id: str) -> List[Note]:
    """Get all notes linked to a specific task"""
    notes = _load_index()
    return [n for n in notes if task_id in n.linked_tasks]

def add_tag(note_id_prefix: str, tag: str) -> Optional[Note]:
    """Add a tag to a note"""
    notes = _load_index()
    note = _match_by_prefix(notes, note_id_prefix)
    
    if not note:
        return None
    
    tag = tag.strip().lower()
    if tag and tag not in note.tags:
        note.tags.append(tag)
        note.modified = _timestamp()
        _save_index(notes)
    
    return note

def remove_tag(note_id_prefix: str, tag: str) -> Optional[Note]:
    """Remove a tag from a note"""
    notes = _load_index()
    note = _match_by_prefix(notes, note_id_prefix)
    
    if not note:
        return None
    
    tag = tag.strip().lower()
    if tag in note.tags:
        note.tags.remove(tag)
        note.modified = _timestamp()
        _save_index(notes)
    
    return note

def get_notes_by_tag(tag: str) -> List[Note]:
    """Get all notes with a specific tag"""
    tag = tag.strip().lower()
    notes = _load_index()
    return [n for n in notes if tag in n.tags]