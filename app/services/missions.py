from database import get_conn
from services.config import get_setting


MISSION_BANKS = {
    "wedding": [
        ("Foto de los protagonistas brindando", "Captura a los protagonistas levantando la copa.", "protagonistas", "foto", 3),
        ("Mirada cómplice", "Una foto natural de los protagonistas, sin que posen demasiado.", "protagonistas", "foto", 3),
        ("Foto divertida de los protagonistas", "Que se note que están disfrutando.", "protagonistas", "foto", 3),
        ("Los protagonistas en la pista", "Una foto bailando o disfrutando la música.", "protagonistas", "foto", 3),
        ("Foto espontánea de los protagonistas", "Sin avisar, pero bonita.", "protagonistas", "foto", 3),
        ("Los protagonistas con una copa", "Momento brindis o celebración.", "protagonistas", "foto", 3),

        ("Foto familiar", "Una imagen bonita de familia o personas cercanas.", "familia", "foto", 3),
        ("Abrazo especial", "Captura un abrazo sincero.", "familia", "foto", 3),
        ("Grupo completo", "Foto de un grupo pasándolo bien.", "familia", "foto", 3),
        ("Foto intergeneracional", "Personas de distintas edades compartiendo momento.", "familia", "foto", 3),
        ("Momento emotivo", "Una escena con emoción real.", "emotiva", "foto", 3),
        ("Sonrisa sincera", "Una sonrisa que merezca ser recordada.", "emotiva", "foto", 3),

        ("Baile improvisado", "Alguien dando todo en la pista.", "fiesta", "foto", 3),
        ("Mesa animada", "Foto de una mesa o grupo en plena celebración.", "fiesta", "foto", 3),
        ("Brindis de grupo", "Foto de varias personas brindando.", "brindis", "foto", 3),
        ("Vídeo de un brindis", "Vídeo corto brindando por los protagonistas.", "brindis", "video", 5),
        ("Vídeo con mensaje bonito", "Graba una felicitación corta.", "emotiva", "video", 5),

        ("Detalle decorativo", "Foto de flores, mesa, luces o algún detalle bonito.", "detalles", "foto", 3),
        ("Zapatos en acción", "Foto divertida de zapatos bailando o caminando.", "detalles", "foto", 3),
        ("Foto artística", "Una foto creativa con encuadre especial.", "detalles", "foto", 3),
        ("Selfie de grupo", "Selfie divertido con varias personas.", "divertida", "foto", 3),
        ("Cara divertida", "Una foto graciosa pero respetuosa.", "divertida", "foto", 3),

        ("Foto que resuma la noche", "La imagen que mejor explique el evento.", "bonus", "foto", 5),
        ("Momento inesperado", "Algo espontáneo que nadie había planeado.", "bonus", "foto", 5),
        ("Vídeo de tu grupo saludando", "Saludad a los protagonistas.", "bonus", "video", 5),
    ],

    "birthday": [
        ("Foto del protagonista", "Captura al protagonista disfrutando de la celebración.", "protagonistas", "foto", 3),
        ("Momento velas", "Foto o vídeo del momento de las velas o la tarta.", "protagonistas", "foto", 4),
        ("Felicitación especial", "Graba una felicitación corta y bonita.", "emotiva", "video", 5),
        ("Abrazo de cumpleaños", "Captura un abrazo sincero.", "emotiva", "foto", 3),
        ("Foto con familia", "Una imagen con personas importantes.", "familia", "foto", 3),
        ("Foto con amigos", "Una imagen de grupo pasándolo bien.", "fiesta", "foto", 3),
        ("Brindis de cumpleaños", "Foto o vídeo brindando por el protagonista.", "brindis", "foto", 3),
        ("Detalle de la decoración", "Foto de globos, tarta, mesa o decoración.", "detalles", "foto", 3),
        ("Selfie divertido", "Selfie con el protagonista o con el grupo.", "divertida", "foto", 3),
        ("Baile o momento animado", "Captura el momento con más energía.", "fiesta", "foto", 3),
        ("Foto que resuma la fiesta", "La imagen que mejor explique el cumpleaños.", "bonus", "foto", 5),
        ("Mensaje de vídeo", "Un vídeo corto con buenos deseos.", "bonus", "video", 5),
    ],

    "company": [
        ("Foto de equipo", "Captura un grupo de compañeros o asistentes.", "protagonistas", "foto", 3),
        ("Momento networking", "Personas conversando o compartiendo ideas.", "fiesta", "foto", 3),
        ("Ponente o presentación", "Foto de una charla, presentación o momento clave.", "detalles", "foto", 3),
        ("Detalle corporativo", "Foto de acreditaciones, cartelería, stand o material.", "detalles", "foto", 3),
        ("Brindis o cierre", "Momento de celebración o cierre del evento.", "brindis", "foto", 3),
        ("Vídeo resumen", "Vídeo corto con ambiente del evento.", "bonus", "video", 5),
        ("Foto espontánea", "Momento natural entre asistentes.", "emotiva", "foto", 3),
        ("Foto divertida de equipo", "Un momento distendido y respetuoso.", "divertida", "foto", 3),
        ("Idea del evento", "Foto que represente el objetivo del encuentro.", "bonus", "foto", 5),
        ("Saludo de grupo", "Vídeo corto saludando a cámara.", "bonus", "video", 5),
    ],

    "party": [
        ("Foto de grupo", "Captura a un grupo disfrutando de la fiesta.", "fiesta", "foto", 3),
        ("Baile destacado", "Alguien dando todo en la pista.", "fiesta", "foto", 3),
        ("Selfie divertido", "Selfie con buen ambiente.", "divertida", "foto", 3),
        ("Brindis", "Foto de un brindis espontáneo.", "brindis", "foto", 3),
        ("Vídeo del ambiente", "Vídeo corto mostrando la energía de la fiesta.", "bonus", "video", 5),
        ("Detalle de decoración", "Foto de luces, mesa, decoración o ambiente.", "detalles", "foto", 3),
        ("Momento inesperado", "Algo espontáneo y divertido.", "bonus", "foto", 5),
        ("Foto que resuma la noche", "La imagen que mejor explique la fiesta.", "bonus", "foto", 5),
    ],

    "communion": [
        ("Foto del protagonista", "Captura al protagonista del día en un momento bonito.", "protagonistas", "foto", 3),
        ("Foto familiar", "Una imagen con familia o personas cercanas.", "familia", "foto", 3),
        ("Abrazo especial", "Un abrazo sincero y bonito.", "emotiva", "foto", 3),
        ("Detalle de la mesa", "Foto de decoración, detalles o recuerdos.", "detalles", "foto", 3),
        ("Foto con amigos", "Una imagen divertida con otros niños o invitados.", "fiesta", "foto", 3),
        ("Momento tarta", "Foto o vídeo del momento dulce.", "bonus", "foto", 4),
        ("Vídeo de felicitación", "Mensaje corto para el protagonista.", "emotiva", "video", 5),
        ("Foto que resuma el día", "La imagen que mejor explique la celebración.", "bonus", "foto", 5),
    ],

    "custom": [
        ("Foto de los protagonistas", "Captura a las personas protagonistas del evento.", "protagonistas", "foto", 3),
        ("Foto de grupo", "Una imagen de grupo disfrutando del momento.", "fiesta", "foto", 3),
        ("Momento emotivo", "Una escena con emoción real.", "emotiva", "foto", 3),
        ("Detalle del evento", "Foto de decoración, objetos o detalles importantes.", "detalles", "foto", 3),
        ("Brindis o celebración", "Foto o vídeo de un momento de celebración.", "brindis", "foto", 3),
        ("Vídeo con mensaje", "Graba un mensaje corto para los organizadores.", "emotiva", "video", 5),
        ("Foto divertida", "Una foto graciosa y respetuosa.", "divertida", "foto", 3),
        ("Foto resumen", "La imagen que mejor explique el evento.", "bonus", "foto", 5),
    ],
}


def get_event_type():
    value = get_setting("EVENT_TYPE", "custom").strip().lower()
    if value not in MISSION_BANKS:
        return "custom"
    return value


def get_default_missions():
    event_type = get_event_type()
    bank = MISSION_BANKS.get(event_type, MISSION_BANKS["custom"])

    # Duplicamos con variaciones genéricas si el banco tiene pocas misiones.
    missions = list(bank)

    while len(missions) < 24:
        missions.extend(bank)

    return missions[:48] if len(missions) >= 48 else missions


def list_missions():
    with get_conn() as conn:
        return conn.execute("""
            SELECT *
            FROM missions
            ORDER BY active DESC, category, title
        """).fetchall()


def create_mission(title, description, category, mission_type, base_points):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO missions (
                title, description, category, mission_type, base_points, active
            )
            VALUES (?, ?, ?, ?, ?, 1)
        """, (title, description, category, mission_type, base_points))


def seed_default_missions():
    with get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) AS n FROM missions").fetchone()["n"]

        if count > 0:
            return

        conn.executemany("""
            INSERT INTO missions (
                title, description, category, mission_type, base_points, active
            )
            VALUES (?, ?, ?, ?, ?, 1)
        """, get_default_missions())


def reset_and_seed_default_missions():
    with get_conn() as conn:
        conn.execute("DELETE FROM guest_missions")
        conn.execute("DELETE FROM missions")

        conn.executemany("""
            INSERT INTO missions (
                title, description, category, mission_type, base_points, active
            )
            VALUES (?, ?, ?, ?, ?, 1)
        """, get_default_missions())
