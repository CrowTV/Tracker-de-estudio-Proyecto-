#Utilidades para calcular y actualizar estadisticas de usuario.

#Este modulo mantiene las reglas de logros, calculo de horas semanales y rachas.


from datetime import datetime, timedelta


# Definiciones de logros y como desbloquearlos.

LOGROS_DETALLES = [
    ("Primer estudio", "Realiza tu primera sesion de estudio."),
    ("5 sesiones completadas", "Completa 5 sesiones en total."),
    ("10 horas estudiadas", "Estudia un total de 10 horas."),
    ("Racha 3 dias", "Estudia 3 dias consecutivos."),
    ("Racha 7 dias", "Estudia 7 dias consecutivos."),
    ("Maraton 2 horas", "Completa una sesion de al menos 2 horas."),
]


def obtener_estadisticas_usuario(usuarios: dict, nombre: str) -> dict:
    
    #Devuelve (o crea) el diccionario de estadisticas para un usuario.
    
    if nombre not in usuarios:
        usuarios[nombre] = {
            "sesiones_totales": 0,
            "minutos_totales": 0,
            "sesiones": [],
            "racha_dias": 0,
            "ultima_sesion": None,
            "ultima_sesion_duracion": 0,
            "logros": [],
        }
    return usuarios[nombre]


def calcular_horas_semana(stats: dict, ahora: datetime | None = None) -> float:
    
    # Calcula las horas estudiadas en los ultimos 7 dias.
    
    if ahora is None:
        ahora = datetime.now()
    semana_atras = ahora - timedelta(days=7)
    minutos = 0
    for s in stats.get("sesiones", []):
        try:
            ts = datetime.fromisoformat(s.get("timestamp"))
        except Exception:
            continue
        if ts >= semana_atras:
            minutos += s.get("duracion_minutos", 0)
    return minutos / 60.0


def actualizar_logros(stats: dict):
    
    #Actualiza la lista de logros en base a las estadisticas actuales.
    
    logros = set(stats.get("logros", []))
    total_minutos = stats.get("minutos_totales", 0)
    sesiones = stats.get("sesiones_totales", 0)
    racha = stats.get("racha_dias", 0)

    def agregar(nombre: str):
        if nombre not in logros:
            logros.add(nombre)

    # Reglas de logros basadas en los detalles definidos.
    
    if sesiones >= 1:
        agregar("Primer estudio")
    if sesiones >= 5:
        agregar("5 sesiones completadas")
    if total_minutos >= 600:
        agregar("10 horas estudiadas")
    if racha >= 3:
        agregar("Racha 3 dias")
    if racha >= 7:
        agregar("Racha 7 dias")

    if stats.get("ultima_sesion_duracion", 0) >= 120:
        agregar("Maraton 2 horas")

    stats["logros"] = sorted(logros)


def obtener_logros_recomendaciones(stats: dict) -> list[str]:
    
    #Devuelve una lista de mensajes que explican como desbloquear logros no obtenidos.
    
    logros_obtenidos = set(stats.get("logros", []))
    recomendaciones = []
    for nombre, descripcion in LOGROS_DETALLES:
        if nombre not in logros_obtenidos:
            recomendaciones.append(f"{nombre}: {descripcion}")
    return recomendaciones


def registrar_sesion(stats: dict, duracion_minutos: int, ahora: datetime | None = None):
    
    #Actualiza estadisticas por una sesion de estudio de duracion dada.
    
    if ahora is None:
        ahora = datetime.now()

    hoy = ahora.date()
    ultima = None
    if stats.get("ultima_sesion"):
        try:
            ultima = datetime.fromisoformat(stats.get("ultima_sesion")).date()
        except Exception:
            ultima = None

    if ultima == hoy:
        pass
    elif ultima == hoy - timedelta(days=1):
        stats["racha_dias"] = stats.get("racha_dias", 0) + 1
    else:
        stats["racha_dias"] = 1

    # Guardamos fecha y hora completos para poder mostrar la ultima sesion con precision.
    
    stats["ultima_sesion"] = ahora.isoformat()
    stats["ultima_sesion_duracion"] = duracion_minutos

    stats["sesiones_totales"] = stats.get("sesiones_totales", 0) + 1
    stats["minutos_totales"] = stats.get("minutos_totales", 0) + duracion_minutos

    sesiones = stats.get("sesiones", [])
    sesiones.append({
        "timestamp": ahora.isoformat(),
        "duracion_minutos": duracion_minutos,
    })

    stats["sesiones"] = sesiones[-200:]

    stats["horas_semana"] = calcular_horas_semana(stats, ahora)

    actualizar_logros(stats)
