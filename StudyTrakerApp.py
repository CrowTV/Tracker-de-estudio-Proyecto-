# visualizacion de la interfaz

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from user_stats import (
    calcular_horas_semana,
    obtener_estadisticas_usuario,
    obtener_logros_recomendaciones,
    registrar_sesion,
)


class StudyTrakerApp:
    DATA_FILE = "tareas.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Study Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2e")

        self.tiempo_restante = 0
        self.corriendo = False
        self.timer_id = None
        self.tarea_seleccionada = None
        self.tareas = []
        self.usuarios = {}
        self.usuario_seleccionado = None
        self.tareas_filtradas = []

        self.cargar_tareas()
        self.crear_interfaz()

    def cargar_tareas(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Actualiza formato: tasks + usuarios
                        self.tareas = data.get("tareas", [])
                        self.usuarios = data.get("usuarios", {})
                    else:
                        # Archivo anterior: una lista de tareas
                        self.tareas = data
                        self.usuarios = {}
            except Exception:
                self.tareas = []
                self.usuarios = {}
        else:
            self.tareas = []
            self.usuarios = {}

    def guardar_tareas(self):
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"tareas": self.tareas, "usuarios": self.usuarios}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el progreso: {e}")

    def crear_interfaz(self):
        
        # seccion de creacion
        
        frame_tarea = tk.LabelFrame(self.root, text="Nueva tarea", bg="#1e1e2e", fg="white")
        frame_tarea.pack(fill=tk.X, padx=10, pady=10)

        campos = [
            ("Nombre del estudiante:", "nombre_estudiante"),
            ("Materia:", "materia"),
            ("Tarea:", "tarea"),
            ("Sesiones necesarias:", "sesiones_necesarias"),
            ("Duracion por defecto (25min):", "duracion_minutos"),
        ]

        self.entradas = {}
        for etiqueta, clave in campos:
            row = tk.Frame(frame_tarea, bg="#1e1e2e")
            row.pack(fill=tk.X, padx=5, pady=3)
            tk.Label(row, text=etiqueta, width=25, anchor="w", bg="#1e1e2e", fg="white").pack(side=tk.LEFT)
            entry = tk.Entry(row, bg="#2e2e3e", fg="white", insertbackground="white")
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entradas[clave] = entry

        boton_agregar = tk.Button(frame_tarea, text="Agregar tarea", command=self.agregar_tarea, bg="#4e4e5e", fg="white", font=("Arial", 11))
        boton_agregar.pack(pady=5)

        # seccion de lista de tareas y progreso
        
        frame_lista = tk.LabelFrame(self.root, text="Progreso de tareas", bg="#1e1e2e", fg="white")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Columna izquierda: lista de tareas + usuarios ---
        frame_izq = tk.Frame(frame_lista, bg="#1e1e2e")
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 2), pady=5)

        frame_tareas = tk.LabelFrame(frame_izq, text="Tareas", bg="#1e1e2e", fg="white")
        frame_tareas.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 2))

        self.lista_tareas = tk.Listbox(frame_tareas, bg="#2e2e3e", fg="white", selectbackground="#5b5bbd", font=("Arial", 11), exportselection=False)
        self.lista_tareas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        self.lista_tareas.bind("<<ListboxSelect>>", self.seleccionar_tarea)

        scrollbar = tk.Scrollbar(frame_tareas, command=self.lista_tareas.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.lista_tareas.config(yscrollcommand=scrollbar.set)

        frame_usuarios = tk.LabelFrame(frame_izq, text="Usuarios", bg="#1e1e2e", fg="white")
        frame_usuarios.pack(fill=tk.BOTH, expand=False, padx=5, pady=(2, 5))

        self.lista_usuarios = tk.Listbox(frame_usuarios, bg="#2e2e3e", fg="white", selectbackground="#5b5bbd", font=("Arial", 10), exportselection=False)
        self.lista_usuarios.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.lista_usuarios.bind("<<ListboxSelect>>", self.seleccionar_usuario)

        # Flag para evitar que la seleccion programatica en usuarios borre la seleccion de la tarea.
        self._suppress_usuario_select = False

        # --- Columna derecha: detalles y logros ---
        frame_der = tk.Frame(frame_lista, bg="#1e1e2e")
        frame_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 10), pady=5)

        frame_detalle = tk.LabelFrame(frame_der, text="Detalles de la tarea", bg="#1e1e2e", fg="white")
        frame_detalle.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 2))

        self.detalle_text = tk.Text(frame_detalle, height=10, bg="#1e1e2e", fg="white", wrap=tk.WORD)
        self.detalle_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.detalle_text.config(state=tk.DISABLED)

        botones_detalle = tk.Frame(frame_detalle, bg="#1e1e2e")
        botones_detalle.pack(fill=tk.X, padx=5, pady=5)

        self.boton_iniciar = tk.Button(botones_detalle, text="Iniciar sesion", command=self.iniciar_estudio, bg="#4e4e5e", fg="white", font=("Arial", 11))
        self.boton_iniciar.pack(side=tk.LEFT, padx=2)

        self.boton_logros = tk.Button(botones_detalle, text="Ver logros", command=self.mostrar_logros_usuario_seleccionado, bg="#4e4e5e", fg="white", font=("Arial", 11))
        self.boton_logros.pack(side=tk.LEFT, padx=2)

        self.boton_pausar = tk.Button(botones_detalle, text="Pausar sesion", command=self.pausar_estudio, bg="#4e4e5e", fg="white", font=("Arial", 11))
        self.boton_pausar.pack(side=tk.LEFT, padx=2)

        self.boton_detener = tk.Button(botones_detalle, text="Detener sesion", command=self.detener_estudio, bg="#4e4e5e", fg="white", font=("Arial", 11))
        self.boton_detener.pack(side=tk.LEFT, padx=2)

        # Campo para ajustar la duracion de la sesion (en minutos)
        duracion_frame = tk.Frame(frame_detalle, bg="#1e1e2e")
        duracion_frame.pack(fill=tk.X, padx=5, pady=(5, 2))
        tk.Label(duracion_frame, text="Duracion (min):", bg="#1e1e2e", fg="white").pack(side=tk.LEFT)
        self.entry_duracion = tk.Entry(duracion_frame, width=5, bg="#2e2e3e", fg="white", insertbackground="white")
        self.entry_duracion.pack(side=tk.LEFT, padx=5)

        self.label_tiempo = tk.Label(frame_detalle, text="Tiempo Restante: 00:00", font=("Arial", 12), bg="#1e1e2e", fg="white")
        self.label_tiempo.pack(pady=5)

        self.actualizar_lista_tareas()
        self.actualizar_lista_usuarios()

    def actualizar_lista_tareas(self):
        self.lista_tareas.delete(0, tk.END)
        # Guardar tarea filtrada para seleccionar correctamente
        self.tareas_filtradas = []
        for tarea in self.tareas:
            if self.usuario_seleccionado and tarea.get("nombre_estudiante") != self.usuario_seleccionado:
                continue
            self.tareas_filtradas.append(tarea)
            progreso = f"{tarea.get('sesiones_completadas', 0)}/{tarea.get('sesiones_necesarias', 0)}"
            item = f"{tarea.get('materia','')} - {tarea.get('tarea','')} ({progreso})"
            self.lista_tareas.insert(tk.END, item)

    def obtener_texto_logros_usuario(self, nombre):
        """Genera el texto de logros/racha/horas para un usuario."""
        stats = obtener_estadisticas_usuario(self.usuarios, nombre)
        horas_semana = calcular_horas_semana(stats)
        logros = stats.get("logros", [])
        recomendaciones = obtener_logros_recomendaciones(stats)

        ultima_sesion_raw = stats.get("ultima_sesion")
        ultima_fecha = "N/A"
        ultima_hora = "N/A"
        if ultima_sesion_raw:
            try:
                dt_ultima = datetime.fromisoformat(ultima_sesion_raw)
                ultima_fecha = dt_ultima.date().isoformat()
                ultima_hora = dt_ultima.time().strftime("%H:%M:%S")
            except Exception:
                ultima_fecha = ultima_sesion_raw

        detalles = (
            f"Usuario: {nombre}\n"
            f"Sesiones totales: {stats.get('sesiones_totales', 0)}\n"
            f"Minutos totales: {stats.get('minutos_totales', 0)}\n"
            f"Horas esta semana: {horas_semana:.2f}\n"
            f"Racha actual: {stats.get('racha_dias', 0)} dia(s)\n"
            f"Ultima sesion: {ultima_fecha} {ultima_hora}\n"
            f"\n"
            f"Logros obtenidos:\n"
        )
        if logros:
            detalles += "\n".join(f"  - {l}" for l in logros)
        else:
            detalles += "  Ninguno\n"

        detalles += "\n\nComo desbloquear logros:\n"
        if recomendaciones:
            detalles += "\n".join(f"  - {r}" for r in recomendaciones)
        else:
            detalles += "  Ya tienes todos los logros!\n"

        return detalles

    def mostrar_logros_usuario_seleccionado(self):
        """Muestra una ventana con los logros del usuario seleccionado o de la tarea seleccionada."""
        nombre = self.usuario_seleccionado
        if not nombre and self.tarea_seleccionada:
            nombre = self.tarea_seleccionada.get("nombre_estudiante", "")

        if not nombre:
            messagebox.showinfo("Logros", "Selecciona un usuario o una tarea para ver sus logros.")
            return

        texto = self.obtener_texto_logros_usuario(nombre)
        messagebox.showinfo("Logros y racha", texto)

    def agregar_tarea(self):
        nombre = self.entradas["nombre_estudiante"].get().strip()
        materia = self.entradas["materia"].get().strip()
        tarea = self.entradas["tarea"].get().strip()
        sesiones_text = self.entradas["sesiones_necesarias"].get().strip()
        duracion_text = self.entradas["duracion_minutos"].get().strip()
        if not (nombre and materia and tarea and sesiones_text.isdigit() and duracion_text.isdigit()):
            messagebox.showwarning("Advertencia", "Completa los campos obligatorios (nombre, materia, tarea, sesiones y duracion).")
            return

        sesiones_necesarias = int(sesiones_text)
        duracion_minutos = int(duracion_text)
        nueva_tarea = {
            "nombre_estudiante": nombre,
            "materia": materia,
            "tarea": tarea,
            "sesiones_necesarias": sesiones_necesarias,
            "sesiones_completadas": 0,
            "fecha_creacion": datetime.now().isoformat(),
            "duracion_minutos": duracion_minutos,
        }

        self.tareas.append(nueva_tarea)
        self.guardar_tareas()
        self.actualizar_lista_tareas()
        self.actualizar_lista_usuarios()
        self.limpiar_campos()

    def limpiar_campos(self):
        for entry in self.entradas.values():
            entry.delete(0, tk.END)

    def seleccionar_tarea(self, event=None):
        seleccion = self.lista_tareas.curselection()
        if not seleccion:
            self.tarea_seleccionada = None
            self.detalle_text.config(state=tk.NORMAL)
            self.detalle_text.delete("1.0", tk.END)
            self.detalle_text.config(state=tk.DISABLED)
            return

        idx = seleccion[0]
        if hasattr(self, "tareas_filtradas") and idx < len(self.tareas_filtradas):
            self.tarea_seleccionada = self.tareas_filtradas[idx]
        else:
            self.tarea_seleccionada = None
        self.actualizar_detalle_tarea()

    def actualizar_detalle_tarea(self):
        # Siempre limpiar el panel de detalles cuando no hay tarea seleccionada.
        if not self.tarea_seleccionada:
            self.detalle_text.config(state=tk.NORMAL)
            self.detalle_text.delete("1.0", tk.END)
            self.detalle_text.config(state=tk.DISABLED)

            # No hay logros/racha en pantalla cuando no hay tarea seleccionada.
            return
            return

        tarea = self.tarea_seleccionada
        nombre = tarea.get("nombre_estudiante", "")

        fecha_creacion_raw = tarea.get('fecha_creacion', '')
        fecha_creacion = fecha_creacion_raw
        hora_creacion = ""
        try:
            dt = datetime.fromisoformat(fecha_creacion_raw)
            fecha_creacion = dt.date().isoformat()
            hora_creacion = dt.time().strftime('%H:%M:%S')
        except Exception:
            # Mantener el valor crudo si no puede parsearse.
            fecha_creacion = fecha_creacion_raw

        detalles = (
            f"Nombre: {nombre}\n"
            f"Materia: {tarea.get('materia','')}\n"
            f"Tarea: {tarea.get('tarea','')}\n"
            f"Sesiones necesarias: {tarea.get('sesiones_necesarias',0)}\n"
            f"Sesiones completadas: {tarea.get('sesiones_completadas',0)}\n"
            f"Progreso: {int((tarea.get('sesiones_completadas',0)/max(1,tarea.get('sesiones_necesarias',1)))*100)}%\n"
            f"Fecha creacion: {fecha_creacion}\n"
            f"Hora creacion: {hora_creacion if hora_creacion else 'N/A'}\n"
        )

        if tarea.get("fecha_termino"):
            detalles += f"Fecha termino: {tarea.get('fecha_termino')}\n"

        self.detalle_text.config(state=tk.NORMAL)
        self.detalle_text.delete("1.0", tk.END)
        self.detalle_text.insert(tk.END, detalles)
        self.detalle_text.see("1.0")
        self.detalle_text.update_idletasks()
        self.detalle_text.config(state=tk.DISABLED)

        # Actualizar duracion sugerida en el campo de entrada
        duracion_sugerida = tarea.get("duracion_minutos", 25)
        try:
            self.entry_duracion.delete(0, tk.END)
            self.entry_duracion.insert(0, str(duracion_sugerida))
        except Exception:
            pass

        # No modificar la seleccion de usuario al mostrar detalles de la tarea.
        # El boton "Ver logros" utilizara el usuario de la tarea seleccionada si no hay usuario seleccionado.
        pass

    def actualizar_lista_usuarios(self):
        """Actualiza la lista de usuarios visibles en el panel de usuarios."""
        if not hasattr(self, "lista_usuarios"):
            return
        self.lista_usuarios.delete(0, tk.END)
        usuarios = sorted({u for u in self.usuarios.keys() if u} | {t.get("nombre_estudiante", "") for t in self.tareas if t.get("nombre_estudiante")})
        for u in usuarios:
            if u:
                self.lista_usuarios.insert(tk.END, u)

    def seleccionar_usuario(self, event=None):
        # Evitar que la seleccion programatica de usuario limpie la seleccion de la tarea.
        if getattr(self, '_suppress_usuario_select', False):
            return

        seleccion = self.lista_usuarios.curselection()
        if not seleccion:
            self.usuario_seleccionado = None
            self.tarea_seleccionada = None
            self.actualizar_detalle_tarea()
            return

        idx = seleccion[0]
        self.usuario_seleccionado = self.lista_usuarios.get(idx)
        self.tarea_seleccionada = None
        # Limpiar seleccion de tarea para que no quede un detalle visible
        self.lista_tareas.selection_clear(0, tk.END)
        self.actualizar_lista_tareas()
        self.actualizar_detalle_tarea()

    def resaltar_usuario_en_listbox(self, nombre):
        """Resalta un usuario en la lista sin actualizar la lista de tareas.

        Esto se usa al seleccionar una tarea para mantener la vista de tareas sin re-renderizar.
        """
        if not hasattr(self, "lista_usuarios"):
            return

        for i in range(self.lista_usuarios.size()):
            if self.lista_usuarios.get(i) == nombre:
                self._suppress_usuario_select = True
                try:
                    self.lista_usuarios.selection_clear(0, tk.END)
                    self.lista_usuarios.selection_set(i)
                    self.lista_usuarios.see(i)
                    self.usuario_seleccionado = nombre
                finally:
                    self._suppress_usuario_select = False
                return

    def seleccionar_usuario_por_nombre(self, nombre, actualizar_logros=True):
        """Selecciona un usuario en la lista de usuarios si existe.

        Si actualizar_logros es False, solo resalta el usuario en la lista sin tocar el panel de logros.
        Esto permite seleccionar una tarea y al mismo tiempo mantener la seccion de logros separada.
        """
        if not hasattr(self, "lista_usuarios"):
            return
        self.actualizar_lista_usuarios()

        for i in range(self.lista_usuarios.size()):
            if self.lista_usuarios.get(i) == nombre:
                self.lista_usuarios.selection_clear(0, tk.END)
                self.lista_usuarios.selection_set(i)
                self.lista_usuarios.see(i)
                self.usuario_seleccionado = nombre
                self.actualizar_lista_tareas()

                if actualizar_logros:
                    self.actualizar_logros_usuario(nombre)

                # Si hay una tarea seleccionada del mismo usuario, mantenerla seleccionada.
                if self.tarea_seleccionada and self.tarea_seleccionada.get("nombre_estudiante") == nombre:
                    for j, tarea in enumerate(getattr(self, "tareas_filtradas", [])):
                        if tarea is self.tarea_seleccionada:
                            self.lista_tareas.selection_set(j)
                            break
                return


    def iniciar_estudio(self):
        if not self.tarea_seleccionada:
            messagebox.showwarning("Advertencia", "Selecciona una tarea primero.")
            return

        if not self.corriendo:
            # Permitir ajuste de duracion por sesion
            duracion = 25
            try:
                duracion = int(self.entry_duracion.get())
                if duracion <= 0:
                    duracion = 25
            except Exception:
                duracion = 25

            self.tiempo_restante = duracion * 60
            self.sesion_duracion_minutos = duracion

            # Guardar como duracion por defecto para la tarea seleccionada
            self.tarea_seleccionada["duracion_minutos"] = duracion
            self.guardar_tareas()

            self.actualizar_timer()
            self.corriendo = True

    def pausar_estudio(self):
        if self.corriendo:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.corriendo = False

    def detener_estudio(self):
        if self.corriendo or self.tiempo_restante > 0:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.corriendo = False
            self.label_tiempo.config(text="Tiempo Restante: 00:00")
            self.tiempo_restante = 0

    def actualizar_timer(self):
        minutos, segundos = divmod(self.tiempo_restante, 60)
        self.label_tiempo.config(text=f"Tiempo Restante: {minutos:02d}:{segundos:02d}")
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.timer_id = self.root.after(1000, self.actualizar_timer)
        else:
            messagebox.showinfo("¡Tiempo terminado!", "¡Has completado tu sesion de estudio!")
            self.corriendo = False

            # contabilizar sesion completada
            if self.tarea_seleccionada:
                self.tarea_seleccionada["sesiones_completadas"] = self.tarea_seleccionada.get("sesiones_completadas", 0) + 1
                duracion = getattr(self, "sesion_duracion_minutos", 25)
                nombre = self.tarea_seleccionada.get("nombre_estudiante", "")

                # Si se completaron todas las sesiones, registrar fecha de termino
                if self.tarea_seleccionada["sesiones_completadas"] >= self.tarea_seleccionada.get("sesiones_necesarias", 0):
                    if not self.tarea_seleccionada.get("fecha_termino"):
                        self.tarea_seleccionada["fecha_termino"] = datetime.now().isoformat()

                stats = obtener_estadisticas_usuario(self.usuarios, nombre)
                registrar_sesion(stats, duracion)
                self.guardar_tareas()
                self.actualizar_lista_tareas()
                self.actualizar_detalle_tarea()
                self.seleccionar_usuario_por_nombre(nombre)
