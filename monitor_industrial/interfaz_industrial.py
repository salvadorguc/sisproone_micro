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

        # Colores del tema industrial
        self.colores = {
            'fondo': '#1a1a1a',
            'panel': '#2d2d2d',
            'texto': '#ffffff',
            'texto_secundario': '#cccccc',
            'accento': '#00ff00',
            'advertencia': '#ffaa00',
            'error': '#ff0000',
            'info': '#0099ff',
            'borde': '#444444'
        }

        # Fuentes
        self.fuente_titulo = ('Arial', 24, 'bold')
        self.fuente_grande = ('Arial', 18, 'bold')
        self.fuente_normal = ('Arial', 12)
        self.fuente_pequena = ('Arial', 10)

    def mostrar(self):
        """Mostrar la interfaz industrial"""
        try:
            self.root = tk.Tk()

            # Inicializar variables tkinter despues de crear root
            self.contador_var = tk.StringVar(value="0")
            self.meta_var = tk.StringVar(value="0")
            self.progreso_var = tk.StringVar(value="0%")
            self.estado_var = tk.StringVar(value="INACTIVO")
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

            self.configurar_ventana()
            self.crear_interfaz()
            self.iniciar_actualizaciones()
            self.logger.info("SUCCESS: Interfaz industrial mostrada")
        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando interfaz: {e}")

    def configurar_ventana(self):
        """Configurar ventana principal"""
        try:
            self.root.title("Monitor Industrial SISPRO")
            self.root.configure(bg=self.colores['fondo'])

            # Fullscreen
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)

            # Configurar teclas de salida
            self.root.bind('<Escape>', self.salir)
            self.root.bind('<F11>', self.toggle_fullscreen)
            self.root.bind('<Control-q>', self.salir)

            # Centrar ventana
            self.root.update_idletasks()
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            self.root.geometry(f"{width}x{height}+0+0")

        except Exception as e:
            self.logger.error(f"ERROR: Error configurando ventana: {e}")

    def crear_interfaz(self):
        """Crear interfaz principal"""
        try:
            # Frame principal
            main_frame = tk.Frame(self.root, bg=self.colores['fondo'])
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Crear paneles
            self.crear_panel_superior(main_frame)
            self.crear_panel_central(main_frame)
            self.crear_panel_receta(main_frame)
            self.crear_panel_inferior(main_frame)
            self.crear_panel_estado(main_frame)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando interfaz: {e}")

    def crear_panel_superior(self, parent):
        """Crear panel superior con configuracion de estacion"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X, pady=(0, 10))

            # Frame principal horizontal
            main_frame = tk.Frame(panel, bg=self.colores['panel'])
            main_frame.pack(fill=tk.X, pady=10, padx=20)

            # Lado izquierdo: Titulo
            titulo = tk.Label(
                main_frame,
                text="MONITOR INDUSTRIAL SISPRO",
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

            # Boton cambiar estacion (pequeño)
            btn_cambiar = tk.Button(
                config_frame,
                text="Cambiar",
                font=self.fuente_pequena,
                fg=self.colores['texto'],
                bg=self.colores['borde'],
                command=self.seleccionar_estacion,
                width=10
            )
            btn_cambiar.grid(row=0, column=2, padx=5)

            # Boton cerrar orden (protegido)
            btn_cerrar = tk.Button(
                config_frame,
                text="CERRAR ORDEN",
                font=self.fuente_pequena,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                command=self.cerrar_orden,
                width=12
            )
            btn_cerrar.grid(row=0, column=3, padx=10)

            # Estado del sistema
            tk.Label(
                config_frame,
                text="Estado:",
                font=self.fuente_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).grid(row=1, column=0, padx=5, sticky=tk.E)

            tk.Label(
                config_frame,
                textvariable=self.estado_var,
                font=self.fuente_normal,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=1, column=1, columnspan=2, padx=5, sticky=tk.W)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel superior: {e}")

    def crear_panel_central(self, parent):
        """Crear panel central con ordenes de fabricacion"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # Titulo del panel
            tk.Label(
                panel,
                text="ORDENES DE FABRICACION",
                font=self.fuente_titulo,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(pady=20)

            # Frame para lista de ordenes y detalles
            contenido_frame = tk.Frame(panel, bg=self.colores['panel'])
            contenido_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Panel izquierdo: Lista de ordenes
            ordenes_frame = tk.Frame(contenido_frame, bg=self.colores['fondo'], relief=tk.SUNKEN, bd=2)
            ordenes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

            tk.Label(
                ordenes_frame,
                text="Ordenes Asignadas",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['fondo']
            ).pack(pady=10)

            # Listbox para ordenes
            self.lista_ordenes = tk.Listbox(
                ordenes_frame,
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                selectbackground=self.colores['accento'],
                selectmode=tk.SINGLE,
                height=15
            )
            self.lista_ordenes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.lista_ordenes.bind('<<ListboxSelect>>', self.on_orden_seleccionada)

            # Panel derecho: Detalles de produccion
            detalles_frame = tk.Frame(contenido_frame, bg=self.colores['fondo'], relief=tk.SUNKEN, bd=2)
            detalles_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            tk.Label(
                detalles_frame,
                text="Produccion Actual",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['fondo']
            ).pack(pady=10)

            # Informacion de la orden actual
            info_orden = tk.Frame(detalles_frame, bg=self.colores['fondo'])
            info_orden.pack(pady=10)

            tk.Label(
                info_orden,
                text="Orden:",
                font=self.fuente_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['fondo']
            ).grid(row=0, column=0, padx=10, sticky=tk.W)

            tk.Label(
                info_orden,
                textvariable=self.orden_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).grid(row=0, column=1, padx=10, sticky=tk.W)

            tk.Label(
                info_orden,
                text="UPC:",
                font=self.fuente_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['fondo']
            ).grid(row=1, column=0, padx=10, sticky=tk.W)

            tk.Label(
                info_orden,
                textvariable=self.upc_var,
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['fondo']
            ).grid(row=1, column=1, padx=10, sticky=tk.W)

            # Contador principal
            contador_frame = tk.Frame(detalles_frame, bg=self.colores['fondo'])
            contador_frame.pack(expand=True, pady=20)

            # Contador actual
            tk.Label(
                contador_frame,
                text="CONTADOR",
                font=self.fuente_grande,
                fg=self.colores['texto_secundario'],
                bg=self.colores['fondo']
            ).pack()

            tk.Label(
                contador_frame,
                textvariable=self.contador_var,
                font=('Arial', 48, 'bold'),
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=10)

            # Meta y progreso
            meta_frame = tk.Frame(detalles_frame, bg=self.colores['fondo'])
            meta_frame.pack(pady=10)

            # Meta
            tk.Label(
                meta_frame,
                text="META:",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['fondo']
            ).grid(row=0, column=0, padx=10, sticky=tk.W)

            tk.Label(
                meta_frame,
                textvariable=self.meta_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).grid(row=0, column=1, padx=10, sticky=tk.W)

            # Progreso
            tk.Label(
                meta_frame,
                text="PROGRESO:",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['fondo']
            ).grid(row=1, column=0, padx=10, sticky=tk.W)

            tk.Label(
                meta_frame,
                textvariable=self.progreso_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).grid(row=1, column=1, padx=10, sticky=tk.W)

            # Barra de progreso
            self.progreso_barra = ttk.Progressbar(
                detalles_frame,
                length=400,
                mode='determinate',
                style='Industrial.Horizontal.TProgressbar'
            )
            self.progreso_barra.pack(pady=10)

            # Configurar estilo de la barra de progreso
            self.configurar_estilo_progreso()

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel central: {e}")

    def crear_panel_receta(self, parent):
        """Crear panel de receta de la orden"""
        try:
            self.panel_receta = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            self.panel_receta.pack(fill=tk.X, pady=(0, 10))

            # Titulo del panel
            tk.Label(
                self.panel_receta,
                text="MATERIALES DE LA ORDEN",
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(pady=10)

            # Area de texto para la receta
            self.receta_text = tk.Text(
                self.panel_receta,
                height=8,
                font=self.fuente_pequena,
                fg=self.colores['texto'],
                bg=self.colores['fondo'],
                wrap=tk.WORD,
                state=tk.DISABLED
            )
            self.receta_text.pack(fill=tk.X, padx=20, pady=(0, 10))

            # Scrollbar para el texto
            scrollbar = tk.Scrollbar(self.panel_receta, orient=tk.VERTICAL, command=self.receta_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.receta_text.config(yscrollcommand=scrollbar.set)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel receta: {e}")

    def crear_panel_inferior(self, parent):
        """Crear panel inferior con botones de control"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X, pady=(0, 10))

            # Botones de control
            botones_frame = tk.Frame(panel, bg=self.colores['panel'])
            botones_frame.pack(pady=15)

            # Boton validar UPC (principal)
            btn_upc = tk.Button(
                botones_frame,
                text="VALIDAR UPC",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['accento'],
                relief=tk.RAISED,
                bd=3,
                command=self.validar_upc,
                width=25,
                height=2
            )
            btn_upc.grid(row=0, column=0, padx=10, pady=5)


            # Boton sincronizar
            btn_sincronizar = tk.Button(
                botones_frame,
                text="SINCRONIZAR",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['info'],
                relief=tk.RAISED,
                bd=2,
                command=self.sincronizar_ahora,
                width=15,
                height=1
            )
            btn_sincronizar.grid(row=1, column=0, padx=10, pady=5)

            # Boton salir
            btn_salir = tk.Button(
                botones_frame,
                text="SALIR",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                relief=tk.RAISED,
                bd=2,
                command=self.salir,
                width=15,
                height=1
            )
            btn_salir.grid(row=1, column=1, padx=10, pady=5)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel inferior: {e}")

    def crear_panel_estado(self, parent):
        """Crear panel de estado del Pico"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X)

            # Estado del Pico
            estado_frame = tk.Frame(panel, bg=self.colores['panel'])
            estado_frame.pack(pady=10)

            # Estado Pico
            tk.Label(
                estado_frame,
                text="Estado Pico:",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=0, padx=10, sticky=tk.W)

            tk.Label(
                estado_frame,
                textvariable=self.estado_pico_var,
                font=self.fuente_normal,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=1, padx=10, sticky=tk.W)

            # Tiempo inactivo
            tk.Label(
                estado_frame,
                text="Tiempo inactivo:",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=2, padx=10, sticky=tk.W)

            tk.Label(
                estado_frame,
                textvariable=self.tiempo_inactivo_var,
                font=self.fuente_normal,
                fg=self.colores['advertencia'],
                bg=self.colores['panel']
            ).grid(row=0, column=3, padx=10, sticky=tk.W)

            # Última sincronización
            tk.Label(
                estado_frame,
                text="Última sincronización:",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=4, padx=10, sticky=tk.W)

            tk.Label(
                estado_frame,
                textvariable=self.ultima_sincronizacion_var,
                font=self.fuente_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).grid(row=0, column=5, padx=10, sticky=tk.W)

            # Última lectura del Pico
            tk.Label(
                estado_frame,
                text="Última lectura Pico:",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=1, column=0, padx=10, sticky=tk.W)

            tk.Label(
                estado_frame,
                textvariable=self.ultima_lectura_var,
                font=self.fuente_normal,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=1, column=1, padx=10, sticky=tk.W)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel de estado: {e}")

    def configurar_estilo_progreso(self):
        """Configurar estilo de la barra de progreso"""
        try:
            style = ttk.Style()
            style.theme_use('clam')

            style.configure(
                'Industrial.Horizontal.TProgressbar',
                background=self.colores['accento'],
                troughcolor=self.colores['borde'],
                borderwidth=2,
                lightcolor=self.colores['accento'],
                darkcolor=self.colores['accento']
            )

        except Exception as e:
            self.logger.error(f"ERROR: Error configurando estilo progreso: {e}")

    def iniciar_actualizaciones(self):
        """Iniciar actualizaciones automaticas de la interfaz"""
        try:
            # Cargar ordenes si hay estacion seleccionada
            if self.monitor.estacion_actual:
                self.cargar_ordenes()

            self.actualizar_interfaz()
            self.actualizar_reloj()
            self.actualizar_semaforo()
            self.root.after(self.monitor.config.update_interval, self.iniciar_actualizaciones)
        except Exception as e:
            self.logger.error(f"ERROR: Error en actualizaciones: {e}")

    def actualizar_interfaz(self):
        """Actualizar elementos de la interfaz"""
        try:
            # Actualizar estado del sistema
            estado = self.monitor.estado.estado_actual
            if hasattr(estado, 'value'):
                self.estado_var.set(estado.value)
            else:
                self.estado_var.set(str(estado))

            # Actualizar información de la estación
            if self.monitor.estacion_actual:
                self.estacion_var.set(self.monitor.estacion_actual.get('nombre', 'N/A'))

            # Actualizar informacion de la orden
            if self.monitor.orden_actual:
                self.orden_var.set(self.monitor.orden_actual.get('ordenFabricacion', 'N/A'))
                self.upc_var.set(self.monitor.orden_actual.get('ptUPC', 'N/A'))

                # Actualizar meta y progreso
                meta = self.monitor.orden_actual.get('cantidadFabricar', 0)
                self.meta_var.set(str(meta))

                if meta > 0:
                    progreso = (self.monitor.lecturas_acumuladas / meta) * 100
                    self.progreso_var.set(f"{progreso:.1f}%")
                    self.progreso_barra['value'] = progreso
                else:
                    self.progreso_var.set("0%")
                    self.progreso_barra['value'] = 0
            else:
                self.orden_var.set('N/A')
                self.upc_var.set('N/A')
                self.meta_var.set('0')
                self.progreso_var.set("0%")
                self.progreso_barra['value'] = 0

            # Actualizar contador
            self.contador_var.set(str(self.monitor.lecturas_acumuladas))

            # Actualizar última sincronización
            if self.monitor.ultima_sincronizacion:
                self.ultima_sincronizacion_var.set(
                    self.monitor.ultima_sincronizacion.strftime("%H:%M:%S")
                )

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando interfaz: {e}")

    def mostrar_receta(self, receta):
        """Mostrar receta de la orden en el panel"""
        try:
            if not self.receta_text or not receta:
                return

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

            self.receta_text.insert(1.0, texto_receta)
            self.receta_text.config(state=tk.DISABLED)

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando receta: {e}")

    def actualizar_contador(self, valor: int):
        """Actualizar contador en tiempo real"""
        try:
            self.contador_var.set(str(valor))

            # Actualizar progreso si hay meta
            if self.monitor.orden_actual:
                meta = self.monitor.orden_actual.get('cantidadFabricar', 0)
                if meta > 0:
                    progreso = (valor / meta) * 100
                    self.progreso_var.set(f"{progreso:.1f}%")
                    self.progreso_barra['value'] = progreso

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando contador: {e}")

    def actualizar_avance(self, avance: Dict[str, Any]):
        """Actualizar avance de la orden"""
        try:
            if avance:
                cantidad_pendiente = avance.get('cantidadPendiente', 0)
                avance_porcentaje = avance.get('avance', 0) * 100

                self.progreso_var.set(f"{avance_porcentaje:.1f}%")
                self.progreso_barra['value'] = avance_porcentaje

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando avance: {e}")

    def actualizar_estado_pico(self, estado: Dict[str, Any]):
        """Actualizar estado del Pico"""
        try:
            if estado:
                self.estado_pico_var.set(estado.get('estado', 'DESCONECTADO'))
                self.tiempo_inactivo_var.set(f"{estado.get('tiempo_inactivo', 0)}s")

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando estado Pico: {e}")

    def mostrar_seleccion_estacion(self, estaciones: List[Dict]) -> Optional[Dict]:
        """Mostrar diálogo de selección de estación"""
        try:
            # Crear ventana de selección
            ventana = tk.Toplevel(self.root)
            ventana.title("Seleccionar Estación")
            ventana.configure(bg=self.colores['fondo'])
            ventana.attributes('-topmost', True)

            # Centrar ventana
            ventana.geometry("600x400")
            ventana.transient(self.root)
            ventana.grab_set()

            # Frame principal
            frame = tk.Frame(ventana, bg=self.colores['fondo'])
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Titulo
            tk.Label(
                frame,
                text="SELECCIONAR ESTACION DE TRABAJO",
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=15)

            # Lista de estaciones
            lista_frame = tk.Frame(frame, bg=self.colores['fondo'])
            lista_frame.pack(fill=tk.BOTH, expand=True, pady=20)

            # Crear lista
            lista = tk.Listbox(
                lista_frame,
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                selectbackground=self.colores['accento'],
                height=10
            )
            lista.pack(fill=tk.BOTH, expand=True)

            # Agregar estaciones a la lista
            for estacion in estaciones:
                texto = f"{estacion['nombre']} - {estacion.get('descripcion', '')}"
                lista.insert(tk.END, texto)

            # Variable para resultado
            resultado = [None]

            def seleccionar():
                seleccion = lista.curselection()
                if seleccion:
                    resultado[0] = estaciones[seleccion[0]]
                    ventana.destroy()

            def cancelar():
                ventana.destroy()

            # Bindings para interaccion
            lista.bind('<Double-Button-1>', lambda e: seleccionar())
            lista.bind('<Return>', lambda e: seleccionar())
            ventana.bind('<Escape>', lambda e: cancelar())

            # Botones
            botones_frame = tk.Frame(frame, bg=self.colores['fondo'])
            botones_frame.pack(pady=20)

            tk.Button(
                botones_frame,
                text="SELECCIONAR",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['accento'],
                command=seleccionar,
                width=15
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="CANCELAR",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                command=cancelar,
                width=15
            ).pack(side=tk.LEFT, padx=10)

            # Esperar a que se cierre la ventana
            ventana.wait_window()

            return resultado[0]

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando seleccion de estacion: {e}")
            return None

    def mostrar_seleccion_orden(self, ordenes: List[Dict]) -> Optional[Dict]:
        """Mostrar diálogo de selección de orden"""
        try:
            # Crear ventana de selección
            ventana = tk.Toplevel(self.root)
            ventana.title("Seleccionar Orden")
            ventana.configure(bg=self.colores['fondo'])
            ventana.attributes('-topmost', True)

            # Centrar ventana
            ventana.geometry("800x500")
            ventana.transient(self.root)
            ventana.grab_set()

            # Frame principal
            frame = tk.Frame(ventana, bg=self.colores['fondo'])
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # Titulo
            tk.Label(
                frame,
                text="SELECCIONAR ORDEN DE FABRICACION",
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=15)

            # Lista de ordenes
            lista_frame = tk.Frame(frame, bg=self.colores['fondo'])
            lista_frame.pack(fill=tk.BOTH, expand=True, pady=20)

            # Crear lista
            lista = tk.Listbox(
                lista_frame,
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                selectbackground=self.colores['accento'],
                height=12
            )
            lista.pack(fill=tk.BOTH, expand=True)

            # Agregar ordenes a la lista
            for orden in ordenes:
                texto = f"{orden['ordenFabricacion']} - {orden.get('ptDescripcion', '')} - Cantidad: {orden.get('cantidadFabricar', 0)}"
                lista.insert(tk.END, texto)

            # Variable para resultado
            resultado = [None]

            def seleccionar():
                seleccion = lista.curselection()
                if seleccion:
                    resultado[0] = ordenes[seleccion[0]]
                    ventana.destroy()

            def cancelar():
                ventana.destroy()

            # Bindings para interaccion
            lista.bind('<Double-Button-1>', lambda e: seleccionar())
            lista.bind('<Return>', lambda e: seleccionar())
            ventana.bind('<Escape>', lambda e: cancelar())

            # Botones
            botones_frame = tk.Frame(frame, bg=self.colores['fondo'])
            botones_frame.pack(pady=20)

            tk.Button(
                botones_frame,
                text="SELECCIONAR",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['accento'],
                command=seleccionar,
                width=15
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="CANCELAR",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                command=cancelar,
                width=15
            ).pack(side=tk.LEFT, padx=10)

            # Esperar a que se cierre la ventana
            ventana.wait_window()

            return resultado[0]

        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando seleccion de orden: {e}")
            return None

    def on_orden_seleccionada(self, event):
        """Manejar seleccion de orden desde la lista"""
        try:
            seleccion = self.lista_ordenes.curselection()
            if seleccion and hasattr(self, 'ordenes_disponibles'):
                index = seleccion[0]
                orden = self.ordenes_disponibles[index]
                self.monitor.orden_actual = orden
                self.orden_var.set(orden['ordenFabricacion'])
                self.upc_var.set(orden.get('ptUPC', 'N/A'))
                self.meta_var.set(str(orden.get('cantidadFabricar', 0)))
                self.monitor.estado.cambiar_estado(EstadoSistema.ESPERANDO_UPC)
                self.logger.info(f"SUCCESS: Orden seleccionada: {orden['ordenFabricacion']} - UPC: {orden.get('ptUPC', 'N/A')}")
        except Exception as e:
            self.logger.error(f"ERROR: Error en seleccion de orden: {e}")

    def cargar_ordenes(self):
        """Cargar ordenes de la estacion actual"""
        try:
            if not self.monitor.estacion_actual:
                return

            ordenes = self.monitor.sispro.obtener_ordenes_asignadas(
                self.monitor.estacion_actual['id']
            )

            # Filtrar solo ordenes pendientes (no completadas y no cerradas)
            ordenes_pendientes = [
                orden for orden in ordenes
                if orden.get('cantidadPendiente', 0) > 0 and not orden.get('isClosed', False)
            ]

            self.ordenes_disponibles = ordenes_pendientes
            self.lista_ordenes.delete(0, tk.END)

            if not ordenes_pendientes:
                self.lista_ordenes.insert(tk.END, "No hay ordenes pendientes")
                return

            for orden in ordenes_pendientes:
                pt = orden.get('pt', '')
                desc = orden.get('ptDescripcion', '')[:40]  # Limitar descripcion
                cantidad = orden.get('cantidadFabricar', 0)
                pendiente = orden.get('cantidadPendiente', 0)
                upc = orden.get('ptUPC', '')
                texto = f"OF: {orden['ordenFabricacion']} | PT: {pt} | UPC: {upc} | {desc} ({pendiente}/{cantidad} pzs)"
                self.lista_ordenes.insert(tk.END, texto)

        except Exception as e:
            self.logger.error(f"ERROR: Error cargando ordenes: {e}")

    def seleccionar_estacion(self):
        """Seleccionar estacion de trabajo"""
        try:
            self.monitor.seleccionar_estacion()
            # Cargar ordenes de la nueva estacion
            self.cargar_ordenes()
        except Exception as e:
            self.logger.error(f"ERROR: Error seleccionando estacion: {e}")
            messagebox.showerror("Error", f"Error seleccionando estacion: {e}")

    def seleccionar_orden(self):
        """Seleccionar orden de fabricacion"""
        try:
            self.monitor.seleccionar_orden()
        except Exception as e:
            self.logger.error(f"ERROR: Error seleccionando orden: {e}")
            messagebox.showerror("Error", f"Error seleccionando orden: {e}")

    def validar_upc(self):
        """Validar codigo UPC"""
        try:
            upc = simpledialog.askstring(
                "Validar UPC",
                "Ingrese el codigo UPC:",
                parent=self.root
            )

            if upc:
                if self.monitor.validar_upc(upc):
                    messagebox.showinfo("Exito", "UPC valido. Produccion iniciada.")
                else:
                    messagebox.showerror("Error", "UPC invalido. Verifique el codigo.")

        except Exception as e:
            self.logger.error(f"ERROR: Error validando UPC: {e}")
            messagebox.showerror("Error", f"Error validando UPC: {e}")

    def cerrar_orden(self):
        """Cerrar orden actual con proteccion por PIN"""
        try:
            if not self.orden_actual:
                messagebox.showwarning("Advertencia", "No hay orden seleccionada")
                return

            # Solicitar PIN de seguridad
            pin_dialog = tk.Toplevel(self.root)
            pin_dialog.title("Cerrar Orden - Seguridad")
            pin_dialog.geometry("350x200")
            pin_dialog.resizable(False, False)
            pin_dialog.transient(self.root)
            pin_dialog.grab_set()

            # Centrar ventana
            pin_dialog.update_idletasks()
            x = (pin_dialog.winfo_screenwidth() // 2) - (350 // 2)
            y = (pin_dialog.winfo_screenheight() // 2) - (200 // 2)
            pin_dialog.geometry(f"350x200+{x}+{y}")

            # Configurar colores
            pin_dialog.configure(bg=self.colores['panel'])

            # Titulo
            tk.Label(
                pin_dialog,
                text="CERRAR ORDEN",
                font=self.fuente_grande,
                fg=self.colores['error'],
                bg=self.colores['panel']
            ).pack(pady=10)

            # Advertencia
            tk.Label(
                pin_dialog,
                text="Esta accion cerrara la orden de fabricacion",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).pack(pady=5)

            tk.Label(
                pin_dialog,
                text=f"Orden: {self.orden_actual['ordenFabricacion']}",
                font=self.fuente_normal,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(pady=5)

            # Campo de PIN
            tk.Label(
                pin_dialog,
                text="Ingrese PIN de seguridad:",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).pack(pady=10)

            pin_entry = tk.Entry(
                pin_dialog,
                font=self.fuente_grande,
                show="*",
                width=15,
                justify=tk.CENTER
            )
            pin_entry.pack(pady=5)
            pin_entry.focus()

            # Variable para resultado
            resultado = {'confirmado': False}

            def validar_pin():
                pin_ingresado = pin_entry.get()
                if pin_ingresado == "314151":
                    resultado['confirmado'] = True
                    pin_dialog.destroy()
                else:
                    messagebox.showerror("Error", "PIN incorrecto")
                    pin_entry.delete(0, tk.END)
                    pin_entry.focus()

            def cancelar():
                pin_dialog.destroy()

            # Botones
            botones_frame = tk.Frame(pin_dialog, bg=self.colores['panel'])
            botones_frame.pack(pady=20)

            tk.Button(
                botones_frame,
                text="CANCELAR",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['borde'],
                command=cancelar,
                width=10
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="CONFIRMAR",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                command=validar_pin,
                width=10
            ).pack(side=tk.LEFT, padx=10)

            # Bind Enter key
            pin_entry.bind('<Return>', lambda e: validar_pin())
            pin_dialog.bind('<Escape>', lambda e: cancelar())

            # Esperar resultado
            pin_dialog.wait_window()

            # Ejecutar cierre si PIN correcto
            if resultado['confirmado'] and self.monitor:
                self.monitor.finalizar_orden()
                messagebox.showinfo("Exito", "Orden cerrada correctamente.")
                self.logger.info("SUCCESS: Orden cerrada con PIN correcto")

        except Exception as e:
            self.logger.error(f"ERROR: Error cerrando orden: {e}")
            messagebox.showerror("Error", f"Error cerrando orden: {e}")

    def sincronizar_ahora(self):
        """Sincronizar datos ahora"""
        try:
            self.monitor.sincronizar_lecturas()
            messagebox.showinfo("Exito", "Datos sincronizados correctamente.")
        except Exception as e:
            self.logger.error(f"ERROR: Error sincronizando: {e}")
            messagebox.showerror("Error", f"Error sincronizando: {e}")

    def toggle_fullscreen(self, event=None):
        """Alternar modo fullscreen"""
        try:
            self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        except Exception as e:
            self.logger.error(f"ERROR: Error alternando fullscreen: {e}")

    def salir(self, event=None):
        """Salir de la aplicacion"""
        try:
            if messagebox.askyesno("Confirmar", "Salir del Monitor Industrial?"):
                self.monitor.detener()
                self.root.quit()
        except Exception as e:
            self.logger.error(f"ERROR: Error saliendo: {e}")
            self.root.quit()

    def actualizar_reloj(self):
        """Actualizar reloj en tiempo real"""
        try:
            from datetime import datetime
            ahora = datetime.now()
            self.reloj_var.set(ahora.strftime("%H:%M:%S"))
        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando reloj: {e}")

    def actualizar_semaforo(self):
        """Actualizar semáforo según tiempo desde última lectura"""
        try:
            if not self.ultima_lectura_timestamp:
                # Sin lecturas
                self.semaforo_label.config(fg=self.colores['error'])  # Rojo
                return

            from datetime import datetime, timedelta
            ahora = datetime.now()
            tiempo_transcurrido = ahora - self.ultima_lectura_timestamp

            if tiempo_transcurrido > timedelta(minutes=30):
                # Más de 30 minutos - Rojo
                self.semaforo_label.config(fg=self.colores['error'])
            elif tiempo_transcurrido > timedelta(minutes=15):
                # Entre 15-30 minutos - Amarillo
                self.semaforo_label.config(fg=self.colores['advertencia'])
            else:
                # Menos de 15 minutos - Verde
                self.semaforo_label.config(fg=self.colores['accento'])

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando semáforo: {e}")

    def actualizar_ultima_lectura(self, timestamp):
        """Actualizar timestamp de última lectura del Pico"""
        try:
            self.ultima_lectura_timestamp = timestamp

            # Actualizar texto en interfaz
            if timestamp:
                from datetime import datetime
                hora_lectura = timestamp.strftime("%H:%M:%S")
                self.ultima_lectura_var.set(hora_lectura)
            else:
                self.ultima_lectura_var.set("N/A")

        except Exception as e:
            self.logger.error(f"ERROR: Error actualizando última lectura: {e}")
