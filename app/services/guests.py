import secrets
import re
import csv
import io
from database import get_conn
from datetime import datetime


def slugify(text):
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9áéíóúñü]+", "-", text)
    text = text.strip("-")
    return text[:20] or "invitado"


def generate_code(name):
    prefix = slugify(name).upper()
    random_part = secrets.token_hex(2).upper()
    return f"{prefix}-{random_part}"


def list_guests():
    with get_conn() as conn:
        return conn.execute("""
            SELECT *
            FROM guests
            ORDER BY table_name, group_name, name, surname
        """).fetchall()


def create_guest(name, surname="", alias="", table_name="", group_name=""):
    code = generate_code(alias or name)

    with get_conn() as conn:
        conn.execute("""
            INSERT INTO guests (
                name, surname, alias, table_name, group_name, code, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name.strip(),
            surname.strip(),
            alias.strip(),
            table_name.strip(),
            group_name.strip(),
            code,
            datetime.now().isoformat(timespec="seconds")
        ))


def import_guests_from_csv(content):
    text = content.decode("utf-8-sig")

    sample = text[:2048]

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ";" if ";" in sample else ","

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    imported = 0
    skipped = 0

    for row in reader:
        # Normaliza cabeceras por si vienen con espacios
        row = {
            (k or "").strip().lower(): (v or "").strip()
            for k, v in row.items()
        }

        name = row.get("nombre", "")

        if not name:
            skipped += 1
            continue

        surname = row.get("apellidos", "")
        alias = row.get("alias", "")
        zona = row.get("zona", row.get("mesa", ""))
        grupo = row.get("grupo", "")

        create_guest(
            name=name,
            surname=surname,
            alias=alias,
            table_name=zona,
            group_name=grupo
        )

        imported += 1

    return imported, skipped


def delete_guest(guest_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM guest_missions WHERE guest_id = ?", (guest_id,))
        conn.execute("DELETE FROM uploads WHERE guest_id = ?", (guest_id,))
        conn.execute("DELETE FROM guests WHERE id = ?", (guest_id,))


def update_guest(guest_id, name, surname="", alias="", table_name="", group_name=""):
    with get_conn() as conn:
        conn.execute("""
            UPDATE guests
            SET name = ?,
                surname = ?,
                alias = ?,
                table_name = ?,
                group_name = ?
            WHERE id = ?
        """, (
            name.strip(),
            surname.strip(),
            alias.strip(),
            table_name.strip(),
            group_name.strip(),
            guest_id
        ))
