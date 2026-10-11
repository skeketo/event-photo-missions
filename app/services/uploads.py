import os
import shutil
from pathlib import Path
from datetime import datetime
from database import get_conn

UPLOAD_ROOT = Path("/app/uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "heic", "mp4", "mov"}


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def file_type_from_extension(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    if ext in {"mp4", "mov"}:
        return "video"
    return "foto"


def safe_name(text):
    text = (text or "invitado").lower()
    valid = []
    for ch in text:
        if ch.isalnum():
            valid.append(ch)
        elif ch in [" ", "-", "_"]:
            valid.append("-")
    result = "".join(valid).strip("-")
    while "--" in result:
        result = result.replace("--", "-")
    return result or "invitado"


def get_guest(guest_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM guests WHERE id = ?",
            (guest_id,)
        ).fetchone()


def get_guest_missions_for_upload(guest_id):
    with get_conn() as conn:
        return conn.execute("""
            SELECT 
                gm.id AS assignment_id,
                gm.completed,
                m.id,
                m.title,
                m.description,
                m.category,
                m.mission_type,
                m.base_points
            FROM guest_missions gm
            JOIN missions m ON m.id = gm.mission_id
            WHERE gm.guest_id = ?
            ORDER BY m.category, m.title
        """, (guest_id,)).fetchall()


def save_upload(guest_id, mission_id, upload_file, comment=""):
    guest = get_guest(guest_id)
    if not guest:
        raise ValueError("Invitado no válido")

    original_filename = upload_file.filename or "archivo"
    if not allowed_file(original_filename):
        raise ValueError("Tipo de archivo no permitido")

    now = datetime.now()
    event_folder = now.strftime("%Y-%m-%d")
    guest_folder = safe_name(f"{guest['alias'] or guest['name']}-{guest['code']}")

    target_dir = UPLOAD_ROOT / event_folder / guest_folder
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{now.strftime('%Y%m%d_%H%M%S')}_guest-{guest_id}_mission-{mission_id or 'libre'}.{ext}"
    target_path = target_dir / stored_filename

    with target_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    size_bytes = target_path.stat().st_size
    file_type = file_type_from_extension(original_filename)

    points = 2 if file_type == "video" else 1

    with get_conn() as conn:
        conn.execute("""
            INSERT INTO uploads (
                guest_id, mission_id, original_filename, stored_filename,
                file_path, file_type, mime_type, size_bytes, comment,
                points, favorite, uploaded_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            guest_id,
            mission_id if mission_id else None,
            original_filename,
            stored_filename,
            str(target_path),
            file_type,
            upload_file.content_type,
            size_bytes,
            comment.strip(),
            points,
            now.isoformat(timespec="seconds"),
        ))

        if mission_id:
            already_completed = conn.execute("""
                SELECT completed
                FROM guest_missions
                WHERE guest_id = ? AND mission_id = ?
            """, (guest_id, mission_id)).fetchone()

            if already_completed and already_completed["completed"] == 0:
                conn.execute("""
                    UPDATE guest_missions
                    SET completed = 1, completed_at = ?
                    WHERE guest_id = ? AND mission_id = ?
                """, (
                    now.isoformat(timespec="seconds"),
                    guest_id,
                    mission_id,
                ))

    return target_path
