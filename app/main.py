from pathlib import Path
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from database import init_db, stats
from services.missions import list_missions, create_mission, seed_default_missions, reset_and_seed_default_missions
from services.guests import list_guests, create_guest, delete_guest, import_guests_from_csv, update_guest
from services.assignments import assign_missions_to_all, list_guest_assignments
from services.public import search_guests, get_guest_with_missions
from services.uploads import get_guest, get_guest_missions_for_upload, save_upload
from services.ranking import get_ranking
from services.availability import uploads_are_open, uploads_open_message
from services.admin_uploads import (
    list_uploads,
    list_guests_with_uploads,
    toggle_favorite,
    build_all_uploads_zip,
    build_favorites_zip,
    build_guest_zip,
    build_ranking_csv,
)
from services.cards import generate_cards_pdf, generate_cards_pdf_a4
from services.config import get_setting, get_config, save_config, ALLOWED_EVENT_TYPES
from services.front_cover import generate_front_cover
from services.auth import (
    verify_login,
    require_admin,
    login_response,
    logout_response,
    admin_2fa_secret,
    provisioning_qr_base64,
)

app = FastAPI(title=get_setting("APP_NAME", "Event Photo Missions"))

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    init_db()


def protect_admin(request: Request):
    auth_redirect = require_admin(request)
    if auth_redirect:
        return auth_redirect
    return None


@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "event_date": get_setting("EVENT_DATE", "Event date"),
        },
    )


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_get(request: Request, error: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "error": error,
        },
    )


@app.post("/admin/login")
def admin_login_post(
    username: str = Form(...),
    password: str = Form(...),
    token: str = Form(...),
):
    if verify_login(username, password, token):
        return login_response()

    return RedirectResponse("/admin/login?error=Credenciales o código 2FA incorrectos", status_code=303)


@app.get("/admin/logout")
def admin_logout():
    return logout_response()


@app.get("/admin/2fa", response_class=HTMLResponse)
def admin_2fa(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    return templates.TemplateResponse(
        request=request,
        name="admin/twofa.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "secret": admin_2fa_secret(),
            "qr_base64": provisioning_qr_base64(),
        },
    )


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "stats": stats(),
        },
    )


@app.get("/admin/invitados", response_class=HTMLResponse)
def admin_invitados(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    return templates.TemplateResponse(
        request=request,
        name="admin/guests.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "guests": list_guests(),
        },
    )


@app.post("/admin/invitados/crear")
def admin_invitados_crear(
    request: Request,
    name: str = Form(...),
    surname: str = Form(""),
    alias: str = Form(""),
    table_name: str = Form(""),
    group_name: str = Form(""),
):
    locked = protect_admin(request)
    if locked:
        return locked

    create_guest(name, surname, alias, table_name, group_name)
    return RedirectResponse("/admin/invitados", status_code=303)


@app.post("/admin/invitados/importar")
async def admin_invitados_importar(request: Request, file: UploadFile = File(...)):
    locked = protect_admin(request)
    if locked:
        return locked

    content = await file.read()
    import_guests_from_csv(content)
    return RedirectResponse("/admin/invitados", status_code=303)


@app.post("/admin/invitados/{guest_id}/borrar")
def admin_invitados_borrar(request: Request, guest_id: int):
    locked = protect_admin(request)
    if locked:
        return locked

    delete_guest(guest_id)
    return RedirectResponse("/admin/invitados", status_code=303)


@app.get("/admin/misiones", response_class=HTMLResponse)
def admin_misiones(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    return templates.TemplateResponse(
        request=request,
        name="admin/missions.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "missions": list_missions(),
            "event_type": get_setting("EVENT_TYPE", "custom"),
            "event_hosts": get_setting("EVENT_HOSTS", "los organizadores"),
            "event_label": get_setting("EVENT_LABEL", "evento"),
        },
    )


@app.post("/admin/misiones/crear")
def admin_misiones_crear(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    mission_type: str = Form(...),
    base_points: int = Form(3),
):
    locked = protect_admin(request)
    if locked:
        return locked

    create_mission(title, description, category, mission_type, base_points)
    return RedirectResponse("/admin/misiones", status_code=303)


@app.post("/admin/misiones/cargar-ejemplo")
def admin_misiones_cargar_ejemplo(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    seed_default_missions()
    return RedirectResponse("/admin/misiones", status_code=303)


@app.post("/admin/misiones/recargar-banco")
def admin_misiones_recargar_banco(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    reset_and_seed_default_missions()
    return RedirectResponse("/admin/misiones", status_code=303)


@app.get("/admin/asignaciones", response_class=HTMLResponse)
def admin_asignaciones(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    return templates.TemplateResponse(
        request=request,
        name="admin/assignments.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "assignments": list_guest_assignments(),
        },
    )


@app.post("/admin/asignaciones/generar")
def admin_asignaciones_generar(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    assign_missions_to_all()
    return RedirectResponse("/admin/asignaciones", status_code=303)


@app.get("/admin/subidas", response_class=HTMLResponse)
def admin_subidas(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    return templates.TemplateResponse(
        request=request,
        name="admin/uploads.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "uploads": list_uploads(),
            "guests": list_guests_with_uploads(),
        },
    )


@app.post("/admin/subidas/{upload_id}/favorita")
def admin_subidas_favorita(request: Request, upload_id: int):
    locked = protect_admin(request)
    if locked:
        return locked

    toggle_favorite(upload_id)
    return RedirectResponse("/admin/subidas", status_code=303)


@app.get("/admin/exportar/todo.zip")
def admin_exportar_todo_zip(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    zip_path = build_all_uploads_zip()
    return FileResponse(
        path=str(zip_path),
        filename=zip_path.name,
        media_type="application/zip"
    )


@app.get("/admin/exportar/favoritas.zip")
def admin_exportar_favoritas_zip(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    zip_path = build_favorites_zip()
    return FileResponse(
        path=str(zip_path),
        filename=zip_path.name,
        media_type="application/zip"
    )


@app.get("/admin/exportar/invitado")
def admin_exportar_invitado(request: Request, guest_id: int):
    locked = protect_admin(request)
    if locked:
        return locked

    zip_path = build_guest_zip(guest_id)
    return FileResponse(
        path=str(zip_path),
        filename=zip_path.name,
        media_type="application/zip"
    )


@app.get("/admin/exportar/ranking.csv")
def admin_exportar_ranking_csv(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    csv_path = build_ranking_csv()
    return FileResponse(
        path=str(csv_path),
        filename=csv_path.name,
        media_type="text/csv"
    )


@app.get("/admin/tarjetas", response_class=HTMLResponse)
def admin_tarjetas(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    return templates.TemplateResponse(
        request=request,
        name="admin/cards.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
        },
    )


@app.post("/admin/tarjetas/generar")
def admin_tarjetas_generar(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    generate_cards_pdf()
    return RedirectResponse("/admin/tarjetas", status_code=303)


@app.get("/admin/tarjetas/descargar")
def admin_tarjetas_descargar(request: Request):
    locked = protect_admin(request)
    if locked:
        return locked

    pdf_path = generate_cards_pdf()
    return FileResponse(
        path=str(pdf_path),
        filename=pdf_path.name,
        media_type="application/pdf"
    )


@app.get("/subir", response_class=HTMLResponse)
def subir(request: Request, guest_id: int = 0, error: str = ""):
    if not uploads_are_open():
        return templates.TemplateResponse(
            request=request,
            name="public/uploads_closed.html",
            context={
                "app_name": get_setting("APP_NAME", "Event Photo Missions"),
                "open_message": uploads_open_message(),
            },
        )

    guest = get_guest(guest_id) if guest_id else None
    missions = get_guest_missions_for_upload(guest_id) if guest else []

    return templates.TemplateResponse(
        request=request,
        name="public/upload.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "guest": guest,
            "missions": missions,
            "error": error,
            "legal_text": get_setting("LEGAL_TEXT", ""),
        },
    )


@app.post("/subir", response_class=HTMLResponse)
async def subir_post(
    request: Request,
    guest_id: int = Form(...),
    mission_id: int = Form(0),
    comment: str = Form(""),
    file: UploadFile = File(...),
):
    if not uploads_are_open():
        return templates.TemplateResponse(
            request=request,
            name="public/uploads_closed.html",
            context={
                "app_name": get_setting("APP_NAME", "Event Photo Missions"),
                "open_message": uploads_open_message(),
            },
            status_code=403,
        )

    try:
        save_upload(guest_id, mission_id, file, comment)
    except Exception as e:
        return RedirectResponse(
            f"/subir?guest_id={guest_id}&error={str(e)}",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="public/upload_success.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "guest_id": guest_id,
        },
    )


@app.get("/misiones", response_class=HTMLResponse)
def misiones(request: Request, q: str = ""):
    guests = search_guests(q) if q else []
    return templates.TemplateResponse(
        request=request,
        name="public/missions_search.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "q": q,
            "guests": guests,
        },
    )


@app.get("/misiones/{guest_id}", response_class=HTMLResponse)
def misiones_invitado(request: Request, guest_id: int):
    guest, missions = get_guest_with_missions(guest_id)

    if not guest:
        return HTMLResponse("<h1>Invitado no encontrado</h1>", status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="public/guest_missions.html",
        context={
            "guest": guest,
            "missions": missions,
        },
    )


@app.get("/ranking", response_class=HTMLResponse)
def ranking(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="public/ranking.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "ranking": get_ranking(),
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/admin/invitados/{guest_id}/editar")
async def admin_edit_guest(
    request: Request,
    guest_id: int,
    name: str = Form(...),
    surname: str = Form(""),
    alias: str = Form(""),
    table_name: str = Form(""),
    group_name: str = Form("")
):
    protect_admin(request)

    update_guest(
        guest_id=guest_id,
        name=name,
        surname=surname,
        alias=alias,
        table_name=table_name,
        group_name=group_name
    )

    return RedirectResponse("/admin/invitados", status_code=303)


@app.post("/admin/tarjetas/generar-a4")
async def admin_generate_cards_pdf_a4(request: Request):
    protect_admin(request)
    generate_cards_pdf_a4()
    return RedirectResponse("/admin/tarjetas", status_code=303)


@app.get("/admin/tarjetas/descargar-a4")
async def admin_download_cards_pdf_a4(request: Request):
    protect_admin(request)

    cards_dir = Path("/app/cards")
    files = sorted(cards_dir.glob("tarjetas-event-photo-missions-a4-4porhoja-*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not files:
        return RedirectResponse("/admin/tarjetas", status_code=303)

    return FileResponse(
        path=str(files[0]),
        media_type="application/pdf",
        filename=files[0].name
    )


@app.get("/admin/configuracion", response_class=HTMLResponse)
def admin_configuracion(request: Request):
    auth_redirect = protect_admin(request)
    if auth_redirect:
        return auth_redirect

    config = get_config()

    return templates.TemplateResponse(
        request=request,
        name="admin/config.html",
        context={
            "app_name": get_setting("APP_NAME", "Event Photo Missions"),
            "config": config,
            "event_types": ALLOWED_EVENT_TYPES,
        },
    )


@app.post("/admin/configuracion")
async def admin_configuracion_guardar(
    request: Request,
    APP_NAME: str = Form(...),
    EVENT_DATE: str = Form(""),
    PUBLIC_BASE_URL: str = Form(""),
    EVENT_TYPE: str = Form("custom"),
    EVENT_HOSTS: str = Form(""),
    EVENT_LABEL: str = Form(""),
    PROTAGONISTS_LABEL: str = Form(""),
    PRIZE_TEXT: str = Form(""),
    LEGAL_TEXT: str = Form(""),
):
    auth_redirect = protect_admin(request)
    if auth_redirect:
        return auth_redirect

    save_config({
        "APP_NAME": APP_NAME,
        "EVENT_DATE": EVENT_DATE,
        "PUBLIC_BASE_URL": PUBLIC_BASE_URL,
        "EVENT_TYPE": EVENT_TYPE,
        "EVENT_HOSTS": EVENT_HOSTS,
        "EVENT_LABEL": EVENT_LABEL,
        "PROTAGONISTS_LABEL": PROTAGONISTS_LABEL,
        "PRIZE_TEXT": PRIZE_TEXT,
        "LEGAL_TEXT": LEGAL_TEXT,
    })

    generate_front_cover()

    return RedirectResponse("/admin/configuracion", status_code=303)
