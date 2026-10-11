from database import get_conn


def search_guests(q):
    q = (q or "").strip()

    if not q:
        return []

    like = f"%{q}%"

    with get_conn() as conn:
        return conn.execute("""
            SELECT *
            FROM guests
            WHERE name LIKE ?
               OR surname LIKE ?
               OR alias LIKE ?
               OR code LIKE ?
            ORDER BY name, surname
            LIMIT 20
        """, (like, like, like, like)).fetchall()


def get_guest_with_missions(guest_id):
    with get_conn() as conn:
        guest = conn.execute("""
            SELECT *
            FROM guests
            WHERE id = ?
        """, (guest_id,)).fetchone()

        if not guest:
            return None, []

        missions = conn.execute("""
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

        return guest, missions
