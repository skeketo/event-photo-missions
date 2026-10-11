# Event Photo Missions

Event Photo Missions is a self-hosted web app for creating photo and video mission games for weddings, birthdays, company events, parties, communions and private celebrations.

Guests can search their name, view assigned missions, upload photos or videos, and check the ranking.

Admin users can manage guests, missions, assignments, uploads, favorite files, exports and printable mission cards.

## Main features

- Public guest mission pages
- Photo and video uploads
- Upload opening date control
- Admin panel with login and TOTP 2FA
- Guest CSV import
- Mission banks by event type
- Automatic mission assignment
- Ranking
- Favorite uploads
- ZIP and CSV exports
- Dynamic front cover with QR code
- Printable A6 cards
- Printable A4 sheets with 4 cards per page
- Configurable event title, date, public URL, prize and legal text

## Supported event types

- wedding
- birthday
- company
- party
- communion
- custom

## Docker

Example docker compose:

~~yaml
services:
  event-photo-missions:
    image: event-photo-missions:latest
    container_name: event-photo-missions
    restart: unless-stopped
    ports:
      - "8093:8000"
    environment:
      APP_NAME: "Event Photo Missions"
      EVENT_DATE: "Event date"
      PUBLIC_BASE_URL: "http://localhost:8093"
      ADMIN_USER: "admin"
      ADMIN_PASSWORD: "change-me"
      SECRET_KEY: "change-this-secret-key"
      ADMIN_2FA_SECRET: ""
      DATABASE_URL: "sqlite:///data/event_photo_missions.db"
      EVENT_TYPE: "wedding"
    volumes:
      - /mnt/user/appdata/event-photo-missions/data:/app/data
      - /mnt/user/appdata/event-photo-missions/uploads:/app/uploads
      - /mnt/user/appdata/event-photo-missions/exports:/app/exports
      - /mnt/user/appdata/event-photo-missions/cards:/app/cards
      - /mnt/user/appdata/event-photo-missions/assets:/app/assets
~~

## First setup

1. Start the container.
2. Open the web UI.
3. Log in using the configured admin credentials.
4. Configure TOTP using the configured ADMIN_2FA_SECRET.
5. Go to Admin > Configuration.
6. Set event type, public URL, title, date, prize text and legal text.
7. Load or regenerate missions according to the event type.
8. Import guests.
9. Generate assignments.
10. Generate printable cards.

## CSV guest import

Expected columns:

~~csv
nombre,apellidos,alias,zona,grupo
~~

Both comma and semicolon separators are supported.

Example:

~~csv
nombre;apellidos;alias;zona;grupo
Laura;Garcia;Laura;Table 1;Friends
Antonio;Lopez;Antonio;Main area;Family
~~

## Security notes

- Change ADMIN_PASSWORD.
- Set a strong SECRET_KEY.
- Set a valid ADMIN_2FA_SECRET.
- Use HTTPS when exposing the app publicly.
- Do not publish /uploads directly through a web server.
- Keep regular backups of data/ and uploads/.

## License

MIT
