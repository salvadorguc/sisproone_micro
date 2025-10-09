#!/usr/bin/env python3
"""
Interfaz Industrial Fullscreen - Monitor de Estacion de Trabajo
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from estado_manager import EstadoSistema

class InterfazIndustrial:
    def __init__(self, monitor):
        self.monitor = monitor
        self.root = None
        self.logger = logging.getLogger(__name__)

        # Variables de la interfaz (se inicializaran despues de crear root)
        self.contador_var = None
        self.meta_var = None
        self.progreso_var = None
        self.estado_var = None
        self.orden_var = None
        self.upc_var = None
        self.estacion_var = None
        self.ultima_sincronizacion_var = None
        self.estado_pico_var = None
        self.tiempo_inactivo_var = None

        # Panel de receta
        self.panel_receta = None
        self.receta_text = None

        # Variables de estado del Pico (se inicializaran despues de crear root)
        self.estado_pico_var = None
        self.tiempo_inactivo_var = None
        self.ultima_sincronizacion_var = None
        self.ultima_lectura_timestamp = None

        # Colores del tema industrial
        self.colores = {
            'fondo': '#f5f5f5',
            'panel': '#e8e8e8',
            'texto': '#0066cc',
            'texto_secundario': '#4d79a3',
            'accento': '#0066cc',
            'advertencia': '#cc6600',
            'error': '#cc0000',
            'success': '#00cc00',
            'info': '#0066cc',
            'borde': '#cccccc',
            # Colores mejorados para botones
            'boton_azul': '#1e40af',      # Azul más oscuro
            'boton_verde': '#059669',     # Verde más oscuro
            'boton_rojo': '#dc2626',      # Rojo más oscuro
            'boton_info': '#0284c7',      # Azul info más oscuro
            # Colores para botones superiores
            'boton_cambiar': '#6b7280',   # Gris para cambiar estación
            'boton_cerrar': '#dc2626',    # Rojo para cerrar orden
            'texto_boton': '#ffffff'      # Texto blanco para botones
        }

        # Fuentes
        self.fuente_titulo = ('Arial', 24, 'bold')
        self.fuente_grande = ('Arial', 18, 'bold')
        self.fuente_normal = ('Arial', 12)
        self.fuente_pequena = ('Arial', 10)
        # Fuentes para footer (más grandes para mejor visibilidad)
        self.fuente_footer_normal = ('Arial', 20)  # Aumentado significativamente
        self.fuente_footer_grande = ('Arial', 28)  # Aumentado significativamente
        self.fuente_footer_contador = ('Arial', 60, 'bold')  # Aumentado significativamente

    def calcular_fuente_dinamica(self, valor_contador):
        """Calcular tamaño de fuente dinámico basado en el valor del contador"""
        try:
            # Tamaño base de la fuente del contador (60)
            tamaño_base = 60  # fuente_footer_contador
            # Aumentar al 80% del valor del contador
            incremento = int(valor_contador * 0.8)
            # Tamaño final (mínimo 60, máximo 120)
            tamaño_final = max(60, min(120, tamaño_base + incremento))
            return ('Arial', tamaño_final, 'bold')
        except Exception as e:
            self.logger.error(f"ERROR: Error calculando fuente dinámica: {e}")
            return self.fuente_footer_contador

    def mostrar(self):
        """Mostrar la interfaz industrial"""
        try:
            self.root = tk.Tk()

            # Inicializar variables tkinter despues de crear root
            self.contador_var = tk.StringVar(value="0")
            self.meta_var = tk.StringVar(value="0/0")
            self.progreso_var = tk.StringVar(value="0%")
            self.estado_var = tk.StringVar(value="Estado: INACTIVO")
            self.orden_var = tk.StringVar(value="N/A")
            self.upc_var = tk.StringVar(value="N/A")
            self.estacion_var = tk.StringVar(value="N/A")
            self.ultima_sincronizacion_var = tk.StringVar(value="N/A")
            self.estado_pico_var = tk.StringVar(value="DESCONECTADO")
            self.tiempo_inactivo_var = tk.StringVar(value="0s")

            # Variables para reloj y semáforo
            self.reloj_var = tk.StringVar(value="00:00:00")
            self.ultima_lectura_var = tk.StringVar(value="N/A")
            self.semaforo_color = tk.StringVar(value="red")

            # Variables internas
            self.orden_actual = None
            self.ultima_lectura_timestamp = None
            self.ultima_recarga_ordenes = None

            self.configurar_ventana()

            # Mostrar loading ANTES de crear la interfaz completa
            self.mostrar_loading()

            # Crear interfaz y seleccionar estación después del loading
            self.root.after(2000, self.inicializar_sistema_completo)

            # Iniciar el bucle principal
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando interfaz: {e}")

    def mostrar_loading(self):
        """Mostrar pantalla de carga"""
        try:
            # Crear frame de loading que cubra toda la pantalla
            self.loading_frame = tk.Frame(self.root, bg=self.colores['fondo'])
            self.loading_frame.place(x=0, y=0, relwidth=1, relheight=1)

            # Título principal
            tk.Label(
                self.loading_frame,
                text="MONITOR SISPRO ONE 1.0",
                font=('Arial', 48, 'bold'),
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(expand=True)

            # Mensaje de carga
            tk.Label(
                self.loading_frame,
                text="Iniciando sistema...",
                font=('Arial', 24),
                fg=self.colores['texto'],
                bg=self.colores['fondo']
            ).pack()

            # Indicador de progreso (puntos animados)
            self.loading_dots = tk.Label(
                self.loading_frame,
                text="",
                font=('Arial', 18),
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            )
            self.loading_dots.pack(pady=20)

            # Iniciar animación de puntos
            self.animar_loading()

            self.logger.info("INFO: Pantalla de carga mostrada")

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando loading: {e}")

    def animar_loading(self):
        """Animar los puntos de carga"""
        try:
            if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
                # Obtener texto actual
                texto_actual = self.loading_dots.cget('text')

                # Ciclar entre 1, 2, 3 puntos
                if texto_actual == "":
                    nuevo_texto = "."
                elif texto_actual == ".":
                    nuevo_texto = ".."
                elif texto_actual == "..":
                    nuevo_texto = "..."
                else:
                    nuevo_texto = ""

                self.loading_dots.config(text=nuevo_texto)

                # Programar siguiente animación
                self.root.after(500, self.animar_loading)

        except Exception as e:
            self.logger.error(f"ERROR: Error animando loading: {e}")

    def inicializar_sistema_completo(self):
        """Inicializar el sistema completo después del loading"""
        try:
            # Ocultar loading
            if hasattr(self, 'loading_frame'):
                self.loading_frame.destroy()
                delattr(self, 'loading_frame')

            # Crear la interfaz completa
            self.crear_interfaz()
            self.iniciar_actualizaciones()
            self.logger.info("SUCCESS: Interfaz industrial mostrada")

            # Seleccionar estación
            self.seleccionar_estacion()

            self.logger.info("SUCCESS: Sistema completamente inicializado")

        except Exception as e:
            self.logger.error(f"ERROR: Error inicializando sistema completo: {e}")

    def configurar_ventana(self):
        """Configurar ventana principal"""
        try:
            self.root.title("Monitor sispro one 1.0")
            self.root.configure(bg=self.colores['fondo'])

            # Configurar ventana para pantalla completa
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)

            # Configurar teclas de salida
            self.root.bind('<Escape>', self.salir)
            self.root.bind('<F11>', self.toggle_fullscreen)
            self.root.bind('<Control-q>', self.salir)

            # Configurar redimensionamiento
            self.root.bind('<Configure>', self.on_window_configure)

            # Forzar actualización del layout después del fullscreen
            self.root.update_idletasks()

        except Exception as e:
            self.logger.error(f"ERROR: Error configurando ventana: {e}")

    def on_window_configure(self, event):
        """Manejar redimensionamiento de ventana"""
        try:
            # Forzar actualización del layout cuando cambia el tamaño
            if event.widget == self.root:
                self.root.update_idletasks()
        except Exception as e:
            self.logger.error(f"ERROR: Error manejando redimensionamiento: {e}")

    def crear_interfaz(self):
        """Crear interfaz principal"""
        try:
            # Frame principal
            main_frame = tk.Frame(self.root, bg=self.colores['fondo'])
            main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

            # Crear paneles
            self.crear_panel_superior(main_frame)
            self.crear_panel_central(main_frame)
            self.crear_panel_inferior(main_frame)
            self.crear_panel_estado(main_frame)

            # Forzar actualización del layout
            main_frame.update_idletasks()

        except Exception as e:
            self.logger.error(f"ERROR: Error creando interfaz: {e}")

    def crear_panel_superior(self, parent):
        """Crear panel superior con configuracion de estacion"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X, pady=(0, 10))

            # Frame principal horizontal
            main_frame = tk.Frame(panel, bg=self.colores['panel'])
            main_frame.pack(fill=tk.X, pady=10, padx=5)

            # Lado izquierdo: Titulo
            titulo = tk.Label(
                main_frame,
                text="MONITOR SISPRO ONE 1.0",
                font=self.fuente_titulo,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            )
            titulo.pack(side=tk.LEFT)

            # Lado derecho: Reloj y configuracion
            right_frame = tk.Frame(main_frame, bg=self.colores['panel'])
            right_frame.pack(side=tk.RIGHT)

            # Reloj en la parte superior derecha
            clock_frame = tk.Frame(right_frame, bg=self.colores['panel'])
            clock_frame.pack(side=tk.TOP, pady=(0, 10))

            tk.Label(
                clock_frame,
                text="HORA:",
                font=self.fuente_pequena,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).pack(side=tk.LEFT)

            tk.Label(
                clock_frame,
                textvariable=self.reloj_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(side=tk.LEFT, padx=5)

            # Semáforo de estado de lecturas
            semaforo_frame = tk.Frame(clock_frame, bg=self.colores['panel'])
            semaforo_frame.pack(side=tk.LEFT, padx=20)

            self.semaforo_label = tk.Label(
                semaforo_frame,
                text="●",
                font=self.fuente_titulo,
                fg=self.colores['error'],
                bg=self.colores['panel']
            )
            self.semaforo_label.pack()

            # Configuracion de estacion
            config_frame = tk.Frame(right_frame, bg=self.colores['panel'])
            config_frame.pack(side=tk.BOTTOM)

            # Estacion actual
            tk.Label(
                config_frame,
                text="Estacion:",
                font=self.fuente_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).grid(row=0, column=0, padx=5, sticky=tk.E)

            tk.Label(
                config_frame,
                textvariable=self.estacion_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=1, padx=5, sticky=tk.W)

            # Boton cerrar orden (protegido)
            self.btn_cerrar_orden = tk.Button(
                config_frame,
                text="CERRAR ORDEN",
                font=self.fuente_pequena,
                fg='white',
                bg=self.colores['boton_cerrar'],
                activebackground='#b91c1c',
                activeforeground='white',
                command=self.cerrar_orden,
                width=15,
                state=tk.DISABLED  # Deshabilitado hasta que se seleccione una orden
            )
            self.btn_cerrar_orden.grid(row=0, column=2, padx=10)

            # Estado del sistema
            tk.Label(
                config_frame,
                textvariable=self.estado_var,
                font=self.fuente_normal,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=1, column=0, columnspan=2, padx=5, sticky=tk.W)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel superior: {e}")

    def crear_panel_central(self, parent):
        """Crear panel central con materiales de la orden"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # Titulo del panel
            tk.Label(
                panel,
                text="MATERIALES DE LA ORDEN DE FABRICACIÓN",
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(pady=10)

            # Frame para el texto de la receta
            text_frame = tk.Frame(panel, bg=self.colores['panel'])
            text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

            # Area de texto para la receta
            self.receta_text = tk.Text(
                text_frame,
                height=12,  # Altura reducida 50% para dar más espacio al footer
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['fondo'],
                wrap=tk.WORD,
                state=tk.DISABLED
            )
            self.receta_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Scrollbar para el texto
            scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.receta_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.receta_text.config(yscrollcommand=scrollbar.set)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel central: {e}")

    def crear_panel_estado(self, parent):
        """Crear panel de estado con informacion de produccion"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # Frame principal
            main_frame = tk.Frame(panel, bg=self.colores['panel'])
            main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=20)

            # Informacion de la orden actual - Lado izquierdo
            info_orden = tk.Frame(main_frame, bg=self.colores['panel'])
            info_orden.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)

            # Orden
            orden_frame = tk.Frame(info_orden, bg=self.colores['panel'])
            orden_frame.pack(fill=tk.X, pady=10)

            tk.Label(
                orden_frame,
                text="ORDEN:",
                font=self.fuente_footer_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).pack(side=tk.LEFT, padx=5)

            tk.Label(
                orden_frame,
                textvariable=self.orden_var,
                font=self.fuente_footer_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(side=tk.LEFT, padx=10)

            # UPC
            upc_frame = tk.Frame(info_orden, bg=self.colores['panel'])
            upc_frame.pack(fill=tk.X, pady=10)

            tk.Label(
                upc_frame,
                text="UPC:",
                font=self.fuente_footer_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).pack(side=tk.LEFT, padx=5)

            tk.Label(
                upc_frame,
                textvariable=self.upc_var,
                font=self.fuente_footer_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).pack(side=tk.LEFT, padx=10)

            # Meta y progreso - Centro
            meta_frame = tk.Frame(main_frame, bg=self.colores['panel'])
            meta_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)

            # Meta
            meta_info_frame = tk.Frame(meta_frame, bg=self.colores['panel'])
            meta_info_frame.pack(fill=tk.X, pady=10)

            tk.Label(
                meta_info_frame,
                text="META (Pendiente/Total):",
                font=self.fuente_footer_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).pack(side=tk.LEFT, padx=5)

            self.meta_label = tk.Label(
                meta_info_frame,
                textvariable=self.meta_var,
                font=self.fuente_footer_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            )
            self.meta_label.pack(side=tk.LEFT, padx=10)

            # Progreso
            progreso_info_frame = tk.Frame(meta_frame, bg=self.colores['panel'])
            progreso_info_frame.pack(fill=tk.X, pady=10)

            tk.Label(
                progreso_info_frame,
                text="PROGRESO:",
                font=self.fuente_footer_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).pack(side=tk.LEFT, padx=5)

            self.progreso_label = tk.Label(
                progreso_info_frame,
                textvariable=self.progreso_var,
                font=self.fuente_footer_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            )
            self.progreso_label.pack(side=tk.LEFT, padx=10)

            # Contador principal - Lado derecho
            contador_frame = tk.Frame(main_frame, bg=self.colores['panel'])
            contador_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20)

            # Contador actual
            tk.Label(
                contador_frame,
                text="CONTADOR",
                font=self.fuente_footer_grande,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).pack(pady=10)

            self.contador_label = tk.Label(
                contador_frame,
                textvariable=self.contador_var,
                font=self.fuente_footer_contador,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            )
            self.contador_label.pack(pady=10)


        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel estado: {e}")

    def crear_panel_inferior(self, parent):
        """Crear panel inferior con botones de accion"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X, pady=(0, 10))

            # Frame para botones
            botones_frame = tk.Frame(panel, bg=self.colores['panel'])
            botones_frame.pack(pady=20)

            # Botones con tamaño uniforme
            boton_width = 15
            boton_height = 2

            # Boton Validar UPC
            btn_validar = tk.Button(
                botones_frame,
                text="VALIDAR UPC",
                font=self.fuente_grande,
                fg='white',
                bg=self.colores['boton_azul'],
                activebackground='#1d4ed8',
                activeforeground='white',
                command=self.validar_upc,
                width=boton_width,
                height=boton_height
            )
            btn_validar.pack(side=tk.LEFT, padx=10)

            # Boton Cambiar Orden
            btn_cambiar_orden = tk.Button(
                botones_frame,
                text="ORDENES",
                font=self.fuente_grande,
                fg='white',
                bg=self.colores['boton_verde'],
                activebackground='#047857',
                activeforeground='white',
                command=self.cambiar_orden,
                width=boton_width,
                height=boton_height
            )
            btn_cambiar_orden.pack(side=tk.LEFT, padx=10)

            # Boton Sincronizar
            btn_sincronizar = tk.Button(
                botones_frame,
                text="SINCRONIZAR",
                font=self.fuente_grande,
                fg='white',
                bg=self.colores['boton_info'],
                activebackground='#0369a1',
                activeforeground='white',
                command=self.sincronizar,
                width=boton_width,
                height=boton_height
            )
            btn_sincronizar.pack(side=tk.LEFT, padx=10)

            # Boton Salir
            btn_salir = tk.Button(
                botones_frame,
                text="SALIR",
                font=self.fuente_grande,
                fg='white',
                bg=self.colores['boton_rojo'],
                activebackground='#b91c1c',
                activeforeground='white',
                command=self.salir,
                width=boton_width,
                height=boton_height
            )
            btn_salir.pack(side=tk.LEFT, padx=10)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel inferior: {e}")


    def mostrar_seleccion_estacion(self, estaciones):
        """Mostrar dialogo de seleccion de estacion"""
        try:
            # Crear ventana modal
            dialog = tk.Toplevel(self.root)
            dialog.title("Seleccionar Estacion")
            dialog.geometry("400x300")
            dialog.configure(bg=self.colores['fondo'])
            dialog.transient(self.root)
            dialog.grab_set()

            # Centrar ventana
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (300 // 2)
            dialog.geometry(f"400x300+{x}+{y}")

            # Titulo
            tk.Label(
                dialog,
                text="ESTACIONES",
                font=self.fuente_titulo,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=20)

            # Lista de estaciones
            lista = tk.Listbox(
                dialog,
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                selectbackground=self.colores['accento'],
                selectmode=tk.SINGLE,
                height=8
            )
            lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            for estacion in estaciones:
                lista.insert(tk.END, f"{estacion['nombre']} - {estacion['descripcion']}")

            # Botones
            botones_frame = tk.Frame(dialog, bg=self.colores['fondo'])
            botones_frame.pack(pady=20)

            resultado = [None]

            def seleccionar():
                seleccion = lista.curselection()
                if seleccion:
                    resultado[0] = estaciones[seleccion[0]]
                    dialog.destroy()

            def cancelar():
                dialog.destroy()

            tk.Button(
                botones_frame,
                text="Seleccionar",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['accento'],
                command=seleccionar
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="Cancelar",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                command=cancelar
            ).pack(side=tk.LEFT, padx=10)

            # Bindings
            lista.bind('<Double-Button-1>', lambda e: seleccionar())
            lista.bind('<Return>', lambda e: seleccionar())
            dialog.bind('<Escape>', lambda e: cancelar())

            # Enfocar lista
            lista.focus_set()

            # Esperar cierre
            dialog.wait_window()

            return resultado[0]

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando seleccion de estacion: {e}")
            return None

    def mostrar_seleccion_orden(self, ordenes):
        """Mostrar dialogo de seleccion de orden"""
        try:
            # Crear ventana modal
            dialog = tk.Toplevel(self.root)
            dialog.title("Seleccionar Orden")
            dialog.geometry("720x400")
            dialog.configure(bg=self.colores['fondo'])
            dialog.transient(self.root)
            dialog.grab_set()

            # Centrar ventana
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (720 // 2)
            y = (dialog.winfo_screenheight() // 2) - (400 // 2)
            dialog.geometry(f"720x400+{x}+{y}")

            # Titulo
            tk.Label(
                dialog,
                text="ORDENES",
                font=self.fuente_titulo,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=20)

            # Lista de ordenes
            lista = tk.Listbox(
                dialog,
                font=self.fuente_pequena,
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                selectbackground=self.colores['accento'],
                selectmode=tk.SINGLE,
                height=12
            )
            lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            for orden in ordenes:
                pt = orden.get('pt', '')
                desc = orden.get('ptDescripcion', '')[:40]
                cantidad = orden.get('cantidadFabricar', 0)
                pendiente = orden.get('cantidadPendiente', 0)
                upc = orden.get('ptUPC', '')
                texto = f"OF: {orden['ordenFabricacion']} | PT: {pt} | UPC: {upc} | {desc} ({pendiente}/{cantidad} pzs)"
                lista.insert(tk.END, texto)

            # Botones
            botones_frame = tk.Frame(dialog, bg=self.colores['fondo'])
            botones_frame.pack(pady=20)

            resultado = [None]

            def seleccionar():
                seleccion = lista.curselection()
                if seleccion:
                    resultado[0] = ordenes[seleccion[0]]
                    dialog.destroy()

            def cancelar():
                dialog.destroy()

            tk.Button(
                botones_frame,
                text="Seleccionar",
                font=self.fuente_normal,
                fg='white',
                bg=self.colores['accento'],
                activebackground='#1d4ed8',
                activeforeground='white',
                command=seleccionar
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="Cancelar",
                font=self.fuente_normal,
                fg='white',
                bg=self.colores['error'],
                activebackground='#b91c1c',
                activeforeground='white',
                command=cancelar
            ).pack(side=tk.LEFT, padx=10)

            # Bindings
            lista.bind('<Double-Button-1>', lambda e: seleccionar())
            lista.bind('<Return>', lambda e: seleccionar())
            dialog.bind('<Escape>', lambda e: cancelar())

            # Enfocar lista
            lista.focus_set()

            # Esperar cierre
            dialog.wait_window()

            return resultado[0]

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando seleccion de orden: {e}")
            return None

    def cargar_ordenes(self):
        """Cargar ordenes de la estacion actual"""
        try:
            if not self.monitor.estacion_actual:
                self.logger.warning("WARNING: No hay estacion actual para cargar ordenes")
                return

            self.logger.info(f"INFO: Cargando ordenes para estacion {self.monitor.estacion_actual['id']}")
            ordenes = self.monitor.sispro.obtener_ordenes_asignadas(
                self.monitor.estacion_actual['id']
            )

            self.logger.info(f"INFO: Se obtuvieron {len(ordenes) if ordenes else 0} ordenes de la API")

            # Log detallado de todas las órdenes obtenidas
            if ordenes:
                self.logger.info("INFO: Lista completa de órdenes de la API:")
                for i, orden in enumerate(ordenes, 1):
                    of = orden.get('ordenFabricacion', 'N/A')
                    pendiente = orden.get('cantidadPendiente', 0)
                    fabricar = orden.get('cantidadFabricar', 0)
                    is_closed = orden.get('isClosed', False)
                    self.logger.info(f"  {i}. OF: {of} | Pendiente: {pendiente}/{fabricar} | Cerrada: {is_closed}")

            # Filtrar solo ordenes pendientes (no completadas y no cerradas)
            ordenes_pendientes = [
                orden for orden in ordenes
                if orden.get('cantidadPendiente', 0) > 0 and not orden.get('isClosed', False)
            ]

            self.logger.info(f"INFO: Se filtraron {len(ordenes_pendientes)} ordenes pendientes")

            # Log detallado de órdenes pendientes filtradas
            if ordenes_pendientes:
                self.logger.info("INFO: Órdenes pendientes filtradas:")
                for i, orden in enumerate(ordenes_pendientes, 1):
                    of = orden.get('ordenFabricacion', 'N/A')
                    pendiente = orden.get('cantidadPendiente', 0)
                    fabricar = orden.get('cantidadFabricar', 0)
                    self.logger.info(f"  {i}. OF: {of} | Pendiente: {pendiente}/{fabricar}")
            else:
                self.logger.warning("WARNING: No se encontraron órdenes pendientes después del filtrado")
            # Guardar órdenes en memoria para el modal
            self.ordenes_disponibles = ordenes_pendientes

            if not ordenes_pendientes:
                self.logger.info("INFO: No hay ordenes pendientes para mostrar")
                return

            self.logger.info(f"SUCCESS: {len(ordenes_pendientes)} ordenes cargadas en memoria para el modal")

        except Exception as e:
            self.logger.error(f"ERROR: Error cargando ordenes: {e}")
            import traceback
            self.logger.error(f"ERROR: Traceback: {traceback.format_exc()}")

    def seleccionar_estacion(self):
        """Seleccionar estacion de trabajo"""
        try:
            self.monitor.seleccionar_estacion()

            # Actualizar la variable de la estación en la interfaz
            if hasattr(self, 'estacion_var') and self.monitor.estacion_actual:
                self.estacion_var.set(self.monitor.estacion_actual.get('nombre', 'N/A'))

            # Cargar ordenes de la nueva estacion inmediatamente
            self.ultima_recarga_ordenes = None  # Forzar recarga
            self.cargar_ordenes()
            self.ultima_recarga_ordenes = datetime.now()
        except Exception as e:
            self.logger.error(f"ERROR: Error seleccionando estacion: {e}")
            messagebox.showerror("Error", f"Error seleccionando estacion: {e}")

    def seleccionar_orden(self):
        """Seleccionar orden de fabricacion"""
        try:
            self.monitor.seleccionar_orden()

            # Actualizar campos del footer con la orden seleccionada
            if self.monitor.orden_actual:
                self.actualizar_campos_orden()
        except Exception as e:
            self.logger.error(f"ERROR: Error seleccionando orden: {e}")
            messagebox.showerror("Error", f"Error seleccionando orden: {e}")

    def actualizar_campos_orden(self):
        """Actualizar campos del footer con la orden seleccionada"""
        try:
            if not self.monitor.orden_actual:
                return

            orden = self.monitor.orden_actual

            # Actualizar Orden
            if hasattr(self, 'orden_var'):
                self.orden_var.set(orden.get('ordenFabricacion', 'N/A'))

            # Actualizar UPC
            if hasattr(self, 'upc_var'):
                self.upc_var.set(orden.get('ptUPC', 'N/A'))

            # Actualizar Meta (pendiente/total)
            if hasattr(self, 'meta_var'):
                pendiente = orden.get('cantidadPendiente', orden.get('cantidadFabricar', 0))
                total = orden.get('cantidadFabricar', 0)
                self.meta_var.set(f"{pendiente}/{total}")

            # Actualizar Progreso (basado en lo completado de lo pendiente)
            if hasattr(self, 'progreso_var'):
                # El progreso se calcula sobre el pendiente_inicial, no sobre el total
                pendiente_inicial = self.monitor.pendiente_inicial if hasattr(self.monitor, 'pendiente_inicial') and self.monitor.pendiente_inicial > 0 else pendiente
                if pendiente_inicial > 0:
                    # Progreso = lecturas completadas / pendiente inicial
                    lecturas_completadas = pendiente_inicial - pendiente
                    progreso = (lecturas_completadas / pendiente_inicial) * 100
                    self.progreso_var.set(f"{progreso:.1f}%")
                else:
                    self.progreso_var.set("100%")

            # Actualizar Contador
            if hasattr(self, 'contador_var'):
                self.contador_var.set("0")

            # Cargar receta de la orden
            self.monitor.cargar_receta_orden()

            # Habilitar boton de cerrar orden
            if hasattr(self, 'btn_cerrar_orden'):
                self.btn_cerrar_orden.config(state=tk.NORMAL)

            self.logger.info(f"SUCCESS: Campos actualizados para orden {orden.get('ordenFabricacion', 'N/A')}")

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando campos de orden: {e}")

    def validar_upc(self):
        """Validar codigo UPC"""
        try:
            self.monitor.validar_upc()
        except Exception as e:
            self.logger.error(f"ERROR: Error validando UPC: {e}")
            messagebox.showerror("Error", f"Error validando UPC: {e}")

    def sincronizar(self):
        """Sincronizar lecturas"""
        try:
            self.monitor.sincronizar_lecturas()
        except Exception as e:
            self.logger.error(f"ERROR: Error sincronizando: {e}")
            messagebox.showerror("Error", f"Error sincronizando: {e}")

    def cerrar_orden(self):
        """Cerrar orden actual"""
        try:
            if not self.monitor.orden_actual:
                messagebox.showwarning("Advertencia", "No hay orden seleccionada")
                return

            # Crear ventana modal para PIN
            dialog = tk.Toplevel(self.root)
            dialog.title("Cerrar Orden")
            dialog.geometry("400x200")
            dialog.configure(bg=self.colores['fondo'])
            dialog.transient(self.root)
            dialog.grab_set()

            # Centrar ventana
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f"400x200+{x}+{y}")

            # Titulo
            tk.Label(
                dialog,
                text="CERRAR ORDEN",
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=10)

            # Campo PIN
            tk.Label(
                dialog,
                text="PIN:",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['fondo']
            ).pack()

            pin_entry = tk.Entry(
                dialog,
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                show="*",
                width=20
            )
            pin_entry.pack(pady=10)
            pin_entry.focus_set()

            # Botones
            botones_frame = tk.Frame(dialog, bg=self.colores['fondo'])
            botones_frame.pack(pady=10)

            def confirmar():
                pin = pin_entry.get()
                if pin == "314151":
                    self.monitor.finalizar_orden(forzar_cierre=True)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "PIN incorrecto")

            def cancelar():
                dialog.destroy()

            tk.Button(
                botones_frame,
                text="Confirmar",
                font=self.fuente_grande,
                fg='white',
                bg=self.colores['accento'],
                activebackground='#1d4ed8',
                activeforeground='white',
                width=12,
                height=2,
                command=confirmar
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="Cancelar",
                font=self.fuente_grande,
                fg='white',
                bg=self.colores['error'],
                activebackground='#b91c1c',
                activeforeground='white',
                width=12,
                height=2,
                command=cancelar
            ).pack(side=tk.LEFT, padx=10)

            # Binding para Enter
            pin_entry.bind('<Return>', lambda e: confirmar())
            dialog.bind('<Escape>', lambda e: cancelar())

        except Exception as e:
            self.logger.error(f"ERROR: Error cerrando orden: {e}")
            messagebox.showerror("Error", f"Error cerrando orden: {e}")

    def cambiar_orden(self):
        """Seleccionar orden - mostrar modal de selección"""
        try:
            # Si hay una orden actual y lecturas pendientes, preguntar si guardar
            if (self.monitor.orden_actual and
                hasattr(self.monitor, 'lecturas_acumuladas') and
                self.monitor.lecturas_acumuladas > 0):

                # Preguntar si desea guardar el progreso
                respuesta = messagebox.askyesno(
                    "Guardar Progreso",
                    f"Hay {self.monitor.lecturas_acumuladas} lecturas pendientes.\n\n"
                    f"¿Desea sincronizar y guardar el progreso antes de cambiar de orden?",
                    icon='question'
                )

                if respuesta:
                    # Sincronizar lecturas pendientes
                    self.monitor.sincronizar_lecturas()
                    self.mostrar_mensaje_exito("Progreso guardado correctamente")

                    # Mostrar loading mientras se recargan las ordenes
                    self.mostrar_loading_recarga_ordenes()

                    # Limpiar ordenes en memoria y forzar recarga desde servidor
                    self.ordenes_disponibles = []
                    self.ultima_recarga_ordenes = None

                    # Recargar ordenes actualizadas desde el servidor
                    self.cargar_ordenes()

                    # Ocultar loading
                    self.ocultar_loading_recarga_ordenes()

                # Limpiar interfaz actual
                self.limpiar_interfaz_orden()

                # Desactivar Pico si está activo
                if hasattr(self.monitor, 'rs485') and self.monitor.rs485:
                    self.monitor.desactivar_pico()

                # Cambiar estado a inactivo
                from estado_manager import EstadoSistema
                self.monitor.estado.cambiar_estado(EstadoSistema.INACTIVO)

            # Mostrar selección de orden (siempre)
            self.monitor.seleccionar_orden()

        except Exception as e:
            self.logger.error(f"ERROR: Error cambiando orden: {e}")
            messagebox.showerror("Error", f"Error cambiando orden: {e}")

    def salir(self):
        """Salir de la aplicacion"""
        try:
            if messagebox.askyesno("Confirmar", "¿Desea salir de la aplicacion?"):
                self.monitor.detener()
                self.root.quit()
        except Exception as e:
            self.logger.error(f"ERROR: Error saliendo: {e}")

    def toggle_fullscreen(self, event=None):
        """Alternar pantalla completa"""
        try:
            self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
            # Forzar actualización del layout después del cambio
            self.root.update_idletasks()
            self.root.update()
        except Exception as e:
            self.logger.error(f"ERROR: Error alternando pantalla completa: {e}")

    def iniciar_actualizaciones(self):
        """Iniciar actualizaciones automaticas de la interfaz"""
        try:
            # Cargar ordenes solo cada 30 segundos
            ahora = datetime.now()
            if self.monitor.estacion_actual:
                if (self.ultima_recarga_ordenes is None or
                    (ahora - self.ultima_recarga_ordenes).total_seconds() >= 30):
                    self.cargar_ordenes()
                    self.ultima_recarga_ordenes = ahora

            self.actualizar_interfaz()
            self.actualizar_reloj()
            self.actualizar_semaforo()

            # Programar siguiente actualizacion
            self.root.after(1000, self.iniciar_actualizaciones)

        except Exception as e:
            self.logger.error(f"ERROR: Error en actualizaciones: {e}")

    def actualizar_interfaz(self):
        """Actualizar interfaz con estado actual"""
        try:
            estado_actual = self.monitor.estado.estado_actual

            if hasattr(estado_actual, 'value'):
                estado_texto = estado_actual.value
            else:
                estado_texto = str(estado_actual)

            self.estado_var.set(f"Estado: {estado_texto}")

            # Actualizar contador
            if self.monitor.contador_actual is not None:
                self.contador_var.set(str(self.monitor.contador_actual))
            else:
                self.contador_var.set("0")

            # Actualizar progreso
            if self.monitor.orden_actual:
                pendiente_inicial = self.monitor.pendiente_inicial if hasattr(self.monitor, 'pendiente_inicial') and self.monitor.pendiente_inicial > 0 else 0
                if pendiente_inicial > 0:
                    # Progreso = contador actual / pendiente inicial
                    progreso = (self.monitor.contador_actual / pendiente_inicial) * 100
                    # Limitar progreso a 100%
                    if progreso > 100:
                        progreso = 100
                    self.progreso_var.set(f"{progreso:.1f}%")
                else:
                    self.progreso_var.set("0%")
            else:
                self.progreso_var.set("0%")

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando interfaz: {e}")

    def mostrar_receta(self, receta):
        """Mostrar receta de la orden en el panel"""
        try:
            self.logger.info(f"INFO: Mostrando receta: {receta is not None}")
            self.logger.info(f"INFO: receta_text existe: {self.receta_text is not None}")
            self.logger.info(f"INFO: panel_receta existe: {self.panel_receta is not None}")

            if not self.receta_text or not receta:
                self.logger.warning("WARNING: No se puede mostrar receta - receta_text o receta es None")
                return

            self.logger.info(f"INFO: Receta tiene {len(receta.get('partidas', []))} partidas")

            # Habilitar edicion temporalmente
            self.receta_text.config(state=tk.NORMAL)
            self.receta_text.delete(1.0, tk.END)

            # Formatear receta
            texto_receta = f"""
ORDEN: {receta.get('ordenFabricacion', 'N/A')}
PRODUCTO: {receta.get('articuloPT', 'N/A')} - {receta.get('descripcionPT', 'N/A')}
CANTIDAD: {receta.get('cantidadPlanificada', 'N/A')}
CAJA: {receta.get('caja', 'N/A')}
CLIENTE: {receta.get('razonSocial', 'N/A')}

MATERIALES REQUERIDOS:
"""

            # Agregar partidas
            for partida in receta.get('partidas', []):
                texto_receta += f"• {partida.get('articuloMP', 'N/A')} - {partida.get('descripcionMP', 'N/A')} (Cant: {partida.get('cantidad', 'N/A')})\n"

            self.logger.info(f"INFO: Texto receta preparado, longitud: {len(texto_receta)}")
            self.receta_text.insert(1.0, texto_receta)
            self.receta_text.config(state=tk.DISABLED)
            self.logger.info("SUCCESS: Receta mostrada correctamente")

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando receta: {e}")
            import traceback
            self.logger.error(f"ERROR: Traceback: {traceback.format_exc()}")

    def actualizar_reloj(self):
        """Actualizar reloj en tiempo real"""
        try:
            ahora = datetime.now()
            tiempo_str = ahora.strftime("%H:%M:%S")
            self.reloj_var.set(tiempo_str)

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando reloj: {e}")

    def actualizar_semaforo(self):
        """Actualizar semaforo de actividad"""
        try:
            if hasattr(self, 'ultima_lectura_timestamp') and self.ultima_lectura_timestamp:
                tiempo_transcurrido = (datetime.now() - self.ultima_lectura_timestamp).total_seconds() / 60

                if tiempo_transcurrido > 30:
                    color = self.colores['error']  # Rojo
                elif tiempo_transcurrido > 15:
                    color = self.colores['advertencia']  # Amarillo
                else:
                    color = self.colores['success']  # Verde
            else:
                color = self.colores['error']  # Rojo por defecto

            self.semaforo_label.config(bg=color)

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando semaforo: {e}")

    def actualizar_ultima_lectura(self, timestamp):
        """Actualizar timestamp de ultima lectura"""
        try:
            self.ultima_lectura_timestamp = timestamp
            tiempo_str = timestamp.strftime("%H:%M:%S")
            self.ultima_lectura_var.set(f"Ultima lectura: {tiempo_str}")

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando ultima lectura: {e}")


    def ocultar(self):
        """Ocultar interfaz"""
        try:
            self.root.withdraw()
            self.logger.info("SUCCESS: Interfaz industrial ocultada")
        except Exception as e:
            self.logger.error(f"ERROR: Error ocultando interfaz: {e}")

    def cerrar(self):
        """Cerrar interfaz"""
        try:
            self.root.destroy()
            self.logger.info("SUCCESS: Interfaz industrial cerrada")
        except Exception as e:
            self.logger.error(f"ERROR: Error cerrando interfaz: {e}")

    def actualizar_estado_pico(self, estado):
        """Actualizar estado del Pico"""
        try:
            if estado and hasattr(self, 'estado_pico_var') and hasattr(self, 'tiempo_inactivo_var'):
                self.estado_pico_var.set(estado.get('estado', 'DESCONECTADO'))
                self.tiempo_inactivo_var.set(f"{estado.get('tiempo_inactivo', 0)}s")
        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando estado Pico: {e}")

    def sincronizar_ahora(self):
        """Sincronizar datos ahora"""
        try:
            self.monitor.sincronizar_lecturas()
            messagebox.showinfo("Exito", "Datos sincronizados correctamente.")
        except Exception as e:
            self.logger.error(f"ERROR: Error sincronizando: {e}")
            messagebox.showerror("Error", f"Error sincronizando: {e}")

    def validar_upc(self):
        """Validar codigo UPC"""
        try:
            from tkinter import simpledialog

            # Crear un dialogo personalizado para evitar problemas de layout
            dialog = tk.Toplevel(self.root)
            dialog.title("Validar UPC")
            dialog.geometry("400x150")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # Centrar el dialogo
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

            # Frame principal
            main_frame = tk.Frame(dialog, bg='white')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Etiqueta
            tk.Label(
                main_frame,
                text="Ingrese el codigo UPC:",
                font=self.fuente_normal,
                bg='white'
            ).pack(pady=(0, 10))

            # Campo de entrada
            upc_var = tk.StringVar()
            entry = tk.Entry(
                main_frame,
                textvariable=upc_var,
                font=self.fuente_normal,
                width=30
            )
            entry.pack(pady=(0, 20))
            entry.focus()

            # Frame para botones
            botones_frame = tk.Frame(main_frame, bg='white')
            botones_frame.pack()

            def validar():
                upc = upc_var.get().strip()
                if upc:
                    if self.monitor.validar_upc(upc):
                        # Mostrar mensaje de exito en la interfaz principal
                        self.mostrar_mensaje_exito("UPC valido. Produccion iniciada.")
                    else:
                        # Mostrar mensaje de error en la interfaz principal
                        self.mostrar_mensaje_error("UPC invalido. Verifique el codigo.")
                dialog.destroy()

            def cancelar():
                dialog.destroy()

            # Botones
            tk.Button(
                botones_frame,
                text="Validar",
                command=validar,
                bg=self.colores['accento'],
                fg='white',
                font=self.fuente_normal,
                width=10
            ).pack(side=tk.LEFT, padx=(0, 10))

            tk.Button(
                botones_frame,
                text="Cancelar",
                command=cancelar,
                bg=self.colores['texto_secundario'],
                fg='white',
                font=self.fuente_normal,
                width=10
            ).pack(side=tk.LEFT)

            # Bind Enter key
            entry.bind('<Return>', lambda e: validar())
            entry.bind('<Escape>', lambda e: cancelar())

        except Exception as e:
            self.logger.error(f"ERROR: Error validando UPC: {e}")
            self.mostrar_mensaje_error(f"Error validando UPC: {e}")

    def sincronizar(self):
        """Sincronizar lecturas"""
        try:
            self.monitor.sincronizar_lecturas()
        except Exception as e:
            self.logger.error(f"ERROR: Error sincronizando: {e}")
            messagebox.showerror("Error", f"Error sincronizando: {e}")

    def salir(self):
        """Salir de la aplicacion"""
        try:
            if messagebox.askyesno("Confirmar", "¿Desea salir de la aplicacion?"):
                self.monitor.detener()
                self.root.quit()
        except Exception as e:
            self.logger.error(f"ERROR: Error saliendo: {e}")

    def actualizar_avance(self, avance):
        """Actualizar avance de la orden"""
        try:
            if avance:
                cantidad_pendiente = avance.get('cantidadPendiente', 0)
                avance_porcentaje = avance.get('avance', 0) * 100

                self.progreso_var.set(f"{avance_porcentaje:.1f}%")

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando avance: {e}")

    def actualizar_contador(self, valor: int):
        """Actualizar contador en tiempo real"""
        try:
            self.contador_var.set(str(valor))

            # Actualizar progreso basado en cantidad pendiente inicial
            if self.monitor.orden_actual:
                pendiente_inicial = self.monitor.pendiente_inicial if hasattr(self.monitor, 'pendiente_inicial') and self.monitor.pendiente_inicial > 0 else 0
                if pendiente_inicial > 0:
                    # Progreso = contador actual / pendiente inicial
                    progreso = (valor / pendiente_inicial) * 100
                    # Limitar progreso a 100%
                    if progreso > 100:
                        progreso = 100
                    self.progreso_var.set(f"{progreso:.1f}%")

            # Actualizar fuente dinámica solo para el contador
            fuente_dinamica = self.calcular_fuente_dinamica(valor)

            # Actualizar fuente del contador (solo el número)
            if hasattr(self, 'contador_label'):
                self.contador_label.config(font=fuente_dinamica)

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando contador: {e}")

    def mostrar_mensaje_exito(self, mensaje: str):
        """Mostrar mensaje de exito sin interferir con el layout"""
        try:
            # Crear un label temporal en la parte superior
            if hasattr(self, 'mensaje_temporal'):
                self.mensaje_temporal.destroy()

            self.mensaje_temporal = tk.Label(
                self.root,
                text=mensaje,
                font=self.fuente_grande,
                fg='white',
                bg='#00cc00',
                relief=tk.RAISED,
                bd=2
            )
            self.mensaje_temporal.place(x=50, y=50, width=400, height=40)

            # Programar eliminacion del mensaje
            self.root.after(3000, self.ocultar_mensaje_temporal)

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando mensaje exito: {e}")

    def mostrar_mensaje_error(self, mensaje: str):
        """Mostrar mensaje de error sin interferir con el layout"""
        try:
            # Crear un label temporal en la parte superior
            if hasattr(self, 'mensaje_temporal'):
                self.mensaje_temporal.destroy()

            self.mensaje_temporal = tk.Label(
                self.root,
                text=mensaje,
                font=self.fuente_grande,
                fg='white',
                bg='#cc0000',
                relief=tk.RAISED,
                bd=2
            )
            self.mensaje_temporal.place(x=50, y=50, width=400, height=40)

            # Programar eliminacion del mensaje
            self.root.after(3000, self.ocultar_mensaje_temporal)

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando mensaje error: {e}")

    def ocultar_mensaje_temporal(self):
        """Ocultar mensaje temporal"""
        try:
            if hasattr(self, 'mensaje_temporal'):
                self.mensaje_temporal.destroy()
                delattr(self, 'mensaje_temporal')
        except Exception as e:
            self.logger.error(f"ERROR: Error ocultando mensaje temporal: {e}")

    def confirmar_conteo_pico(self, conteo_actual: int, salto: int) -> bool:
        """Confirmar si el operador quiere conservar el conteo del Pico"""
        try:
            # Crear diálogo de confirmación
            dialog = tk.Toplevel(self.root)
            dialog.title("Pico No Reiniciado")
            dialog.geometry("500x300")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()

            # Centrar el diálogo
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))

            # Frame principal
            main_frame = tk.Frame(dialog, bg='white')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Título
            tk.Label(
                main_frame,
                text="⚠️ PICO NO REINICIADO",
                font=('Arial', 16, 'bold'),
                fg='#cc6600',
                bg='white'
            ).pack(pady=(0, 20))

            # Mensaje principal
            mensaje = f"""El Pico tiene {conteo_actual} lecturas guardadas de una sesión anterior.

Salto detectado: +{salto} lecturas

¿Qué desea hacer?"""

            tk.Label(
                main_frame,
                text=mensaje,
                font=self.fuente_normal,
                bg='white',
                justify=tk.LEFT
            ).pack(pady=(0, 30))

            # Frame para botones
            botones_frame = tk.Frame(main_frame, bg='white')
            botones_frame.pack()

            resultado = [False]  # Usar lista para poder modificar desde funciones internas

            def conservar_conteo():
                resultado[0] = True
                dialog.destroy()

            def reiniciar_pico():
                resultado[0] = False
                dialog.destroy()

            # Botón Conservar Conteo
            tk.Button(
                botones_frame,
                text="CONSERVAR CONTEO",
                command=conservar_conteo,
                bg='#00cc00',
                fg='white',
                font=self.fuente_normal,
                width=15,
                height=1
            ).pack(side=tk.LEFT, padx=(0, 10))

            # Botón Reiniciar Pico
            tk.Button(
                botones_frame,
                text="REINICIAR PICO",
                command=reiniciar_pico,
                bg='#cc0000',
                fg='white',
                font=self.fuente_normal,
                width=15,
                height=1
            ).pack(side=tk.LEFT)

            # Instrucciones
            tk.Label(
                main_frame,
                text="• CONSERVAR: Continúa con el conteo actual\n• REINICIAR: Reinicia el Pico manualmente y vuelve a validar UPC",
                font=('Arial', 10),
                fg='#666666',
                bg='white',
                justify=tk.LEFT
            ).pack(pady=(20, 0))

            # Esperar respuesta
            dialog.wait_window()

            return resultado[0]

        except Exception as e:
            self.logger.error(f"ERROR: Error en confirmacion conteo Pico: {e}")
            return False

    def limpiar_interfaz_orden(self):
        """Limpiar interfaz cuando se completa una orden"""
        try:
            self.logger.info("INFO: Iniciando limpieza de interfaz de orden")

            # Limpiar variables de la orden actual
            self.orden_actual = None
            self.receta_actual = None

            # Limpiar campos de la interfaz
            if hasattr(self, 'orden_var'):
                self.orden_var.set("N/A")
            if hasattr(self, 'upc_var'):
                self.upc_var.set("N/A")
            if hasattr(self, 'meta_var'):
                self.meta_var.set("0/0")
            if hasattr(self, 'progreso_var'):
                self.progreso_var.set("0%")
            if hasattr(self, 'contador_var'):
                self.contador_var.set("0")

            # Limpiar panel de materiales (receta)
            if hasattr(self, 'receta_text') and self.receta_text:
                self.logger.info("INFO: Limpiando panel de materiales")
                # Habilitar edicion temporalmente
                self.receta_text.config(state=tk.NORMAL)
                self.receta_text.delete(1.0, tk.END)
                self.receta_text.insert(tk.END, "Seleccione una orden para ver los materiales")
                # Volver a deshabilitar
                self.receta_text.config(state=tk.DISABLED)
                self.logger.info("SUCCESS: Panel de materiales limpiado")
            else:
                self.logger.warning("WARNING: receta_text no existe o es None")

            # Nota: La lista de órdenes ahora se maneja solo a través del modal

            # Actualizar estado
            if hasattr(self, 'estado_var'):
                self.estado_var.set("Estado: INACTIVO")

            # Limpiar última lectura
            if hasattr(self, 'ultima_lectura_var'):
                self.ultima_lectura_var.set("Ultima lectura: N/A")

            # Deshabilitar boton de cerrar orden
            if hasattr(self, 'btn_cerrar_orden'):
                self.btn_cerrar_orden.config(state=tk.DISABLED)

            self.logger.info("SUCCESS: Interfaz limpiada para nueva orden")

        except Exception as e:
            self.logger.error(f"ERROR: Error limpiando interfaz orden: {e}")

    def mostrar_loading_recarga_ordenes(self):
        """Mostrar mensaje de loading al recargar ordenes"""
        try:
            # Crear un label temporal en el centro de la pantalla
            if hasattr(self, 'loading_recarga'):
                self.loading_recarga.destroy()

            # Obtener dimensiones de la ventana
            ancho_ventana = self.root.winfo_width()
            alto_ventana = self.root.winfo_height()

            # Dimensiones del loading
            ancho_loading = 400
            alto_loading = 100

            # Calcular posición centrada
            x = (ancho_ventana - ancho_loading) // 2
            y = (alto_ventana - alto_loading) // 2

            self.loading_recarga = tk.Label(
                self.root,
                text="Actualizando ordenes...",
                font=self.fuente_grande,
                fg='white',
                bg=self.colores['accento'],
                relief=tk.RAISED,
                bd=3
            )
            self.loading_recarga.place(x=x, y=y, width=ancho_loading, height=alto_loading)

            # Forzar actualización de la interfaz para mostrar el loading
            self.root.update_idletasks()
            self.root.update()

            self.logger.info("INFO: Loading de recarga de ordenes mostrado")

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando loading recarga ordenes: {e}")

    def ocultar_loading_recarga_ordenes(self):
        """Ocultar mensaje de loading de recarga de ordenes"""
        try:
            if hasattr(self, 'loading_recarga'):
                self.loading_recarga.destroy()
                delattr(self, 'loading_recarga')
                self.logger.info("SUCCESS: Loading de recarga de ordenes ocultado")
        except Exception as e:
            self.logger.error(f"ERROR: Error ocultando loading recarga ordenes: {e}")

