import csv
import zipfile
from pathlib import Path
from datetime import datetime
from database import get_conn
from services.ranking import get_ranking

EXPORTS_DIR = Path("/app/exports")


def list_uploads():
    with get_conn() as conn:
        return conn.execute("""
            SELECT
                u.*,
                g.name,
                g.surname,
                g.alias,
                g.code,
                m.title AS mission_title
            FROM uploads u
            JOIN guests g ON g.id = u.guest_id
            LEFT JOIN missions m ON m.id = u.mission_id
            ORDER BY u.uploaded_at DESC
        """).fetchall()


def list_guests_with_uploads():
    with get_conn() as conn:
        return conn.execute("""
            SELECT DISTINCT
                g.id,
                g.name,
                g.surname,
                g.alias,
                g.code
            FROM guests g
            JOIN uploads u ON u.guest_id = g.id
            ORDER BY g.name, g.surname
        """).fetchall()


def toggle_favorite(upload_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT favorite FROM uploads WHERE id = ?",
            (upload_id,)
        ).fetchone()

        if not row:
            return

        new_value = 0 if row["favorite"] else 1

        conn.execute(
            "UPDATE uploads SET favorite = ? WHERE id = ?",
            (new_value, upload_id)
        )


def _safe(text):
    return (text or "sin-nombre").replace("/", "-").replace("\\", "-")


def _build_zip_from_uploads(uploads, prefix):
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    zip_name = f"{prefix}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
    zip_path = EXPORTS_DIR / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for u in uploads:
            file_path = Path(u["file_path"])

            if not file_path.exists():
                continue

            guest_name = _safe(u["alias"] or u["name"])
            mission = _safe(u["mission_title"] or "subida-libre")
            arcname = f"{guest_name}/{mission}/{u['stored_filename']}"

            zf.write(file_path, arcname)

    return zip_path


def build_all_uploads_zip():
    return _build_zip_from_uploads(
        list_uploads(),
        "event-photo-missions-todo"
    )


def build_favorites_zip():
    uploads = [u for u in list_uploads() if u["favorite"]]
    return _build_zip_from_uploads(
        uploads,
        "event-photo-missions-favoritas"
    )


def build_guest_zip(guest_id):
    with get_conn() as conn:
        uploads = conn.execute("""
            SELECT
                u.*,
                g.name,
                g.surname,
                g.alias,
                g.code,
                m.title AS mission_title
            FROM uploads u
            JOIN guests g ON g.id = u.guest_id
            LEFT JOIN missions m ON m.id = u.mission_id
            WHERE g.id = ?
            ORDER BY u.uploaded_at DESC
        """, (guest_id,)).fetchall()

        guest = conn.execute("""
            SELECT *
            FROM guests
            WHERE id = ?
        """, (guest_id,)).fetchone()

    guest_name = _safe((guest["alias"] or guest["name"]) if guest else "invitado")
    return _build_zip_from_uploads(
        uploads,
        f"event-photo-missions-{guest_name}"
    )


def build_ranking_csv():
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    csv_name = f"ranking-event-photo-missions-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    csv_path = EXPORTS_DIR / csv_name

    rows = get_ranking()

    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "posicion",
            "nombre",
            "apellidos",
            "alias",
            "zona",
            "grupo",
            "fotos",
            "videos",
            "misiones_completadas",
            "puntos",
        ])

        for idx, r in enumerate(rows, start=1):
            writer.writerow([
                idx,
                r["name"],
                r["surname"] or "",
                r["alias"] or "",
                r["table_name"] or "",
                r["group_name"] or "",
                r["photos_count"] or 0,
                r["videos_count"] or 0,
                r["completed_missions"] or 0,
                r["total_points"] or 0,
            ])

    return csv_path
