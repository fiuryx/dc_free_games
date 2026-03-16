# dc_free_games

Bot de Discord que notifica **juegos gratis** en Steam, Epic Games, GOG y Prime Gaming.

## Características

- Detección automática de juegos gratis
- Verificación triple: CheapShark, Epic y GamerPower
- Logs automáticos
- Anti-spam y cooldown de comandos
- Botón para reclamar juego
- Logos de tiendas
- Base de datos local con fecha de última notificación → permite volver a notificar si un juego se repite después de X días

## Comandos

- `!freegames` → Muestra los últimos 5 juegos gratis

## Deploy en Railway

1. Conecta tu repo `dc_free_games` en Railway.
2. Añade variable de entorno: `DISCORD_TOKEN`.
3. Opcional: `CHECK_INTERVAL` (segundos entre búsquedas) y `RESEND_DAYS` (días para volver a notificar un juego repetido).
4. Railway ejecutará automáticamente `python bot/main.py`.