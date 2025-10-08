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
        # Fuentes para footer (25% más grandes)
        self.fuente_footer_normal = ('Arial', 15)  # 12 * 1.25
        self.fuente_footer_grande = ('Arial', 22)  # 18 * 1.25
        self.fuente_footer_contador = ('Arial', 45, 'bold')  # 36 * 1.25

    def mostrar(self):
        """Mostrar la interfaz industrial"""
        try:
            self.root = tk.Tk()

            # Inicializar variables tkinter despues de crear root
            self.contador_var = tk.StringVar(value="0")
            self.meta_var = tk.StringVar(value="0/0")
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
            self.ultima_recarga_ordenes = None

            self.configurar_ventana()
            self.crear_interfaz()
            self.iniciar_actualizaciones()
            self.logger.info("SUCCESS: Interfaz industrial mostrada")

            # Iniciar el bucle principal
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"ERROR: Error mostrando interfaz: {e}")

    def configurar_ventana(self):
        """Configurar ventana principal"""
        try:
            self.root.title("Monitor sispro one 1.0")
            self.root.configure(bg=self.colores['fondo'])

            # Configurar ventana para pantalla completa
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)

            # Eliminar bordes y barra de título
            self.root.overrideredirect(False)  # Mantener barra de título para poder cerrar

            # Configurar teclas de salida
            self.root.bind('<Escape>', self.salir)
            self.root.bind('<F11>', self.toggle_fullscreen)
            self.root.bind('<Control-q>', self.salir)

        except Exception as e:
            self.logger.error(f"ERROR: Error configurando ventana: {e}")

    def crear_interfaz(self):
        """Crear interfaz principal"""
        try:
            # Frame principal
            main_frame = tk.Frame(self.root, bg=self.colores['fondo'])
            main_frame.pack(fill=tk.BOTH, padx=5, pady=5)

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

            # Boton cambiar estacion (pequeño)
            btn_cambiar = tk.Button(
                config_frame,
                text="Cambiar Estacion",
                font=self.fuente_pequena,
                fg=self.colores['texto_boton'],
                bg=self.colores['boton_cambiar'],
                activebackground='#4b5563',
                command=self.seleccionar_estacion,
                width=15
            )
            btn_cambiar.grid(row=0, column=2, padx=5)

            # Boton cerrar orden (protegido)
            btn_cerrar = tk.Button(
                config_frame,
                text="CERRAR ORDEN",
                font=self.fuente_pequena,
                fg=self.colores['texto_boton'],
                bg=self.colores['boton_cerrar'],
                activebackground='#b91c1c',
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
        """Crear panel central con materiales de la orden"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.BOTH, pady=(0, 10))

            # Titulo del panel
            tk.Label(
                panel,
                text="MATERIALES DE LA ORDEN",
                font=self.fuente_grande,  # Mismo tamaño que ÓRDENES ASIGNADAS
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(pady=10)

            # Frame para el texto de la receta
            text_frame = tk.Frame(panel, bg=self.colores['panel'])
            text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Area de texto para la receta
            self.receta_text = tk.Text(
                text_frame,
                height=12,  # Altura aumentada
                font=self.fuente_normal,  # Aumentar fuente 50% (de pequeña a normal)
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

    def crear_panel_receta(self, parent):
        """Crear panel de receta con ordenes asignadas"""
        try:
            self.panel_receta = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            self.panel_receta.pack(fill=tk.X, pady=(0, 10))

            # Titulo del panel
            tk.Label(
                self.panel_receta,
                text="ORDENES ASIGNADAS",
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(pady=10)

            # Frame para lista de ordenes
            ordenes_frame = tk.Frame(self.panel_receta, bg=self.colores['fondo'], relief=tk.SUNKEN, bd=2)
            ordenes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Listbox para ordenes
            self.lista_ordenes = tk.Listbox(
                ordenes_frame,
                font=self.fuente_pequena,  # Disminuir fuente 20%
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                selectbackground=self.colores['accento'],
                selectmode=tk.SINGLE,
                height=4  # Disminuir altura 50%
            )
            self.lista_ordenes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.lista_ordenes.bind('<<ListboxSelect>>', self.on_orden_seleccionada)

            # Scrollbar para la lista
            scrollbar_ordenes = tk.Scrollbar(ordenes_frame, orient=tk.VERTICAL, command=self.lista_ordenes.yview)
            scrollbar_ordenes.pack(side=tk.RIGHT, fill=tk.Y)
            self.lista_ordenes.config(yscrollcommand=scrollbar_ordenes.set)

        except Exception as e:
            self.logger.error(f"ERROR: Error creando panel receta: {e}")

    def crear_panel_estado(self, parent):
        """Crear panel de estado con informacion de produccion"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X, pady=(0, 10))

            # Frame principal
            main_frame = tk.Frame(panel, bg=self.colores['panel'])
            main_frame.pack(fill=tk.X, padx=20, pady=10)

            # Informacion de la orden actual
            info_orden = tk.Frame(main_frame, bg=self.colores['panel'])
            info_orden.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Label(
                info_orden,
                text="Orden:",
                font=self.fuente_footer_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).grid(row=0, column=0, padx=10, sticky=tk.W)

            tk.Label(
                info_orden,
                textvariable=self.orden_var,
                font=self.fuente_footer_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=1, padx=10, sticky=tk.W)

            tk.Label(
                info_orden,
                text="UPC:",
                font=self.fuente_footer_normal,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).grid(row=1, column=0, padx=10, sticky=tk.W)

            tk.Label(
                info_orden,
                textvariable=self.upc_var,
                font=self.fuente_footer_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=1, column=1, padx=10, sticky=tk.W)

            # Contador principal
            contador_frame = tk.Frame(main_frame, bg=self.colores['panel'])
            contador_frame.pack(side=tk.RIGHT, padx=20)

            # Contador actual
            tk.Label(
                contador_frame,
                text="CONTADOR",
                font=self.fuente_footer_grande,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).pack()

            tk.Label(
                contador_frame,
                textvariable=self.contador_var,
                font=self.fuente_footer_contador,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(pady=5)

            # Meta y progreso
            meta_frame = tk.Frame(main_frame, bg=self.colores['panel'])
            meta_frame.pack(side=tk.RIGHT, padx=20)

            # Meta
            tk.Label(
                meta_frame,
                text="META (Pendiente/Total):",
                font=self.fuente_footer_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=0, padx=10, sticky=tk.W)

            tk.Label(
                meta_frame,
                textvariable=self.meta_var,
                font=self.fuente_footer_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=1, padx=10, sticky=tk.W)

            # Progreso
            tk.Label(
                meta_frame,
                text="PROGRESO:",
                font=self.fuente_footer_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=1, column=0, padx=10, sticky=tk.W)

            tk.Label(
                meta_frame,
                textvariable=self.progreso_var,
                font=self.fuente_footer_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=1, column=1, padx=10, sticky=tk.W)


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
                text="CAMBIAR ORDEN",
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
                text="SELECCIONAR ESTACION",
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
            dialog.geometry("600x400")
            dialog.configure(bg=self.colores['fondo'])
            dialog.transient(self.root)
            dialog.grab_set()

            # Centrar ventana
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
            y = (dialog.winfo_screenheight() // 2) - (400 // 2)
            dialog.geometry(f"600x400+{x}+{y}")

            # Titulo
            tk.Label(
                dialog,
                text="SELECCIONAR ORDEN",
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
            self.logger.error(f"ERROR: Error mostrando seleccion de orden: {e}")
            return None

    def on_orden_seleccionada(self, event):
        """Manejar seleccion de orden desde la lista"""
        try:
            # Verificar si hay una lectura activa (bloquear selección solo si está produciendo)
            if (hasattr(self.monitor, 'estado') and
                self.monitor.estado.estado_actual == EstadoSistema.PRODUCIENDO):
                messagebox.showwarning(
                    "Lectura Activa",
                    "Hay una lectura en proceso. Use 'CAMBIAR ORDEN' para cambiar a otra orden."
                )
                return

            seleccion = self.lista_ordenes.curselection()
            if seleccion and hasattr(self, 'ordenes_disponibles'):
                index = seleccion[0]
                orden = self.ordenes_disponibles[index]
                self.monitor.orden_actual = orden
                self.orden_var.set(orden['ordenFabricacion'])
                self.upc_var.set(orden.get('ptUPC', 'N/A'))
                # Mostrar pendiente/total
                pendiente = orden.get('cantidadPendiente', orden.get('cantidadFabricar', 0))
                total = orden.get('cantidadFabricar', 0)
                self.meta_var.set(f"{pendiente}/{total}")
                self.monitor.estado.cambiar_estado(EstadoSistema.ESPERANDO_UPC)

                # Cargar receta de la orden seleccionada
                self.logger.info(f"INFO: Cargando receta para orden seleccionada: {orden['ordenFabricacion']}")
                self.monitor.cargar_receta_orden()

                self.logger.info(f"SUCCESS: Orden seleccionada: {orden['ordenFabricacion']} - UPC: {orden.get('ptUPC', 'N/A')}")
        except Exception as e:
            self.logger.error(f"ERROR: Error en seleccion de orden: {e}")

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
            self.ordenes_disponibles = ordenes_pendientes
            self.lista_ordenes.delete(0, tk.END)

            if not ordenes_pendientes:
                self.lista_ordenes.insert(tk.END, "No hay ordenes pendientes")
                self.logger.info("INFO: No hay ordenes pendientes para mostrar")
                return

            for orden in ordenes_pendientes:
                pt = orden.get('pt', '')
                desc = orden.get('ptDescripcion', '')[:40]  # Limitar descripcion
                cantidad = orden.get('cantidadFabricar', 0)
                pendiente = orden.get('cantidadPendiente', 0)
                upc = orden.get('ptUPC', '')
                texto = f"OF: {orden['ordenFabricacion']} | PT: {pt} | UPC: {upc} | {desc} ({pendiente}/{cantidad} pzs)"
                self.lista_ordenes.insert(tk.END, texto)

            self.logger.info(f"SUCCESS: Se cargaron {len(ordenes_pendientes)} ordenes en la lista")

        except Exception as e:
            self.logger.error(f"ERROR: Error cargando ordenes: {e}")
            import traceback
            self.logger.error(f"ERROR: Traceback: {traceback.format_exc()}")

    def seleccionar_estacion(self):
        """Seleccionar estacion de trabajo"""
        try:
            self.monitor.seleccionar_estacion()
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
        except Exception as e:
            self.logger.error(f"ERROR: Error seleccionando orden: {e}")
            messagebox.showerror("Error", f"Error seleccionando orden: {e}")

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
            dialog.geometry("300x150")
            dialog.configure(bg=self.colores['fondo'])
            dialog.transient(self.root)
            dialog.grab_set()

            # Centrar ventana
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
            y = (dialog.winfo_screenheight() // 2) - (150 // 2)
            dialog.geometry(f"300x150+{x}+{y}")

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
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['accento'],
                command=confirmar
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="Cancelar",
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                command=cancelar
            ).pack(side=tk.LEFT, padx=10)

            # Binding para Enter
            pin_entry.bind('<Return>', lambda e: confirmar())
            dialog.bind('<Escape>', lambda e: cancelar())

        except Exception as e:
            self.logger.error(f"ERROR: Error cerrando orden: {e}")
            messagebox.showerror("Error", f"Error cerrando orden: {e}")

    def cambiar_orden(self):
        """Cambiar orden actual - guardar progreso y limpiar UX"""
        try:
            if not self.monitor.orden_actual:
                messagebox.showwarning("Advertencia", "No hay orden seleccionada")
                return

            # Verificar si hay lecturas pendientes
            if hasattr(self.monitor, 'lecturas_acumuladas') and self.monitor.lecturas_acumuladas > 0:
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

            # Limpiar interfaz actual
            self.limpiar_interfaz_orden()

            # Desactivar Pico si está activo
            if hasattr(self.monitor, 'rs485') and self.monitor.rs485:
                self.monitor.desactivar_pico()

            # Cambiar estado a inactivo
            from estado_manager import EstadoSistema
            self.monitor.estado.cambiar_estado(EstadoSistema.INACTIVO)

            # Mostrar selección de nueva orden
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
                meta = self.monitor.orden_actual.get('cantidadFabricar', 0)
                if meta > 0:
                    progreso = (self.monitor.contador_actual / meta) * 100
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

            # Actualizar progreso basado en cantidad pendiente
            if self.monitor.orden_actual:
                meta_pendiente = self.monitor.orden_actual.get('cantidadPendiente', self.monitor.orden_actual.get('cantidadFabricar', 0))
                if meta_pendiente > 0:
                    progreso = (valor / meta_pendiente) * 100
                    # Limitar progreso a 100%
                    if progreso > 100:
                        progreso = 100
                    self.progreso_var.set(f"{progreso:.1f}%")

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

            # Limpiar selección en la lista de órdenes
            if hasattr(self, 'lista_ordenes') and self.lista_ordenes:
                self.lista_ordenes.selection_clear(0, tk.END)

            # Actualizar estado
            if hasattr(self, 'estado_var'):
                self.estado_var.set("Estado: INACTIVO")

            # Limpiar última lectura
            if hasattr(self, 'ultima_lectura_var'):
                self.ultima_lectura_var.set("Ultima lectura: N/A")

            self.logger.info("SUCCESS: Interfaz limpiada para nueva orden")

        except Exception as e:
            self.logger.error(f"ERROR: Error limpiando interfaz orden: {e}")

