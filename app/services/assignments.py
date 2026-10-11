from database import get_conn

CATEGORY_PLAN = {
    "novios": 2,
    "familia": 1,
    "fiesta": 1,
    "emotiva": 1,
    "detalles": 1,
    "divertida": 1,
    "bonus": 1,
}


def clear_assignments():
    with get_conn() as conn:
        conn.execute("DELETE FROM guest_missions")


def get_mission_usage(conn):
    rows = conn.execute("""
        SELECT mission_id, COUNT(*) AS total
        FROM guest_missions
        GROUP BY mission_id
    """).fetchall()

    return {row["mission_id"]: row["total"] for row in rows}


def pick_missions_for_category(conn, category, amount, used_ids, usage):
    missions = conn.execute("""
        SELECT *
        FROM missions
        WHERE active = 1 AND category = ?
        ORDER BY title
    """, (category,)).fetchall()

    candidates = [m for m in missions if m["id"] not in used_ids]

    candidates.sort(key=lambda m: (usage.get(m["id"], 0), m["title"]))

    return candidates[:amount]


def assign_missions_to_all():
    with get_conn() as conn:
        guests = conn.execute("""
            SELECT *
            FROM guests
            ORDER BY name, surname
        """).fetchall()

        if not guests:
            return 0, "No hay invitados."

        missions_count = conn.execute("""
            SELECT COUNT(*) AS n
            FROM missions
            WHERE active = 1
        """).fetchone()["n"]

        if missions_count == 0:
            return 0, "No hay misiones activas."

        conn.execute("DELETE FROM guest_missions")

        total_assigned = 0

        for guest in guests:
            used_ids = set()
            usage = get_mission_usage(conn)

            selected = []

            for category, amount in CATEGORY_PLAN.items():
                picked = pick_missions_for_category(
                    conn=conn,
                    category=category,
                    amount=amount,
                    used_ids=used_ids,
                    usage=usage,
                )

                for mission in picked:
                    selected.append(mission)
                    used_ids.add(mission["id"])

            for mission in selected:
                conn.execute("""
                    INSERT INTO guest_missions (guest_id, mission_id, completed)
                    VALUES (?, ?, 0)
                """, (guest["id"], mission["id"]))
                total_assigned += 1

        return total_assigned, f"Asignadas {total_assigned} misiones a {len(guests)} invitados."


def list_guest_assignments():
    with get_conn() as conn:
        guests = conn.execute("""
            SELECT *
            FROM guests
            ORDER BY table_name, group_name, name, surname
        """).fetchall()

        result = []

        for guest in guests:
            missions = conn.execute("""
                SELECT m.*
                FROM guest_missions gm
                JOIN missions m ON m.id = gm.mission_id
                WHERE gm.guest_id = ?
                ORDER BY m.category, m.title
            """, (guest["id"],)).fetchall()

            result.append({
                "guest": guest,
                "missions": missions,
            })

        return result
