from database import get_conn


def get_ranking():
    with get_conn() as conn:
        return conn.execute("""
            SELECT
                g.id,
                g.name,
                g.surname,
                g.alias,
                g.code,
                g.table_name,
                g.group_name,

                COUNT(u.id) AS uploads_count,

                SUM(CASE WHEN u.file_type = 'foto' THEN 1 ELSE 0 END) AS photos_count,
                SUM(CASE WHEN u.file_type = 'video' THEN 1 ELSE 0 END) AS videos_count,

                (
                    SELECT COUNT(*)
                    FROM guest_missions gm
                    WHERE gm.guest_id = g.id
                      AND gm.completed = 1
                ) AS completed_missions,

                COALESCE(SUM(u.points), 0)
                +
                (
                    SELECT COUNT(*) * 3
                    FROM guest_missions gm
                    WHERE gm.guest_id = g.id
                      AND gm.completed = 1
                ) AS total_points

            FROM guests g
            LEFT JOIN uploads u ON u.guest_id = g.id
            GROUP BY g.id
            ORDER BY total_points DESC, completed_missions DESC, uploads_count DESC, g.name ASC
        """).fetchall()
