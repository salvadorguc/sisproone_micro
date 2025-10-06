#!/usr/bin/env python3
"""
Monitor Industrial SISPRO - Dashboard con Carga de Trabajo
Versión que simula el dashboard real de SISPRO
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import random
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonitorIndustrialDashboard:
    def __init__(self):
        # Estado del sistema
        self.estacion_actual = None
        self.orden_actual = None
        self.upc_validado = None
        self.lecturas_acumuladas = 0
        self.running = False

        # Datos de prueba - Carga de trabajo asignada
        self.estacion_actual = {
            "id": 10,
            "nombre": "ESTACION 10",
            "coordinador": "Sin coordinador",
            "cuadrante": "Sin cuadrante",
            "ultima_actualizacion": "4:06:22 p.m."
        }

        self.carga_trabajo = [
            {
                "of": "523804",
                "pt": "A6953",
                "descripcion": "P6ME TIN CAB PREMIUM OXFORD",
                "upc": "7506424069539",
                "cantidad": 48,
                "pendiente": 48,
                "avance": 0.0,
                "prioridad": "NORMAL",
                "estatus": "PLANIFICADA",
                "cliente": "A0008",
                "razon_social": "TIENDAS SORIANA",
                "caja": "IGG0137 - CAJA",
                "dimensiones": "QUARRY 49 X 33 X 17",
                "materiales": [
                    {"mp": "HCW0735", "descripcion": "FLEX - WILSON ESTUCHE CABALLERO TIN AFELPADO 6 PARES", "cantidad": 1},
                    {"mp": "HGG0475", "descripcion": "GANCHO GOTA ROJO", "cantidad": 1},
                    {"mp": "IGG0045", "descripcion": "PLASTIFLECHA DE 1 PULGADA", "cantidad": 1},
                    {"mp": "IGG0167", "descripcion": "ETIQUETA RECTANGULAR TRANSPARENTE 45 * 65 MM", "cantidad": 1},
                    {"mp": "IGG0032", "descripcion": "ETIQUETA 49 X 51 BLANCA", "cantidad": 1},
                    {"mp": "CW7101", "descripcion": "PUE - NO SHOW CABALLERO AFELPADO POLIESTER CON PIQUE T40/44 OXFORD VIVOS JASPE", "cantidad": 6}
                ]
            },
            {
                "of": "523805",
                "pt": "A6954",
                "descripcion": "BOLSA C/6 DAM JASPE UNI",
                "upc": "7506424069546",
                "cantidad": 24,
                "pendiente": 24,
                "avance": 0.0,
                "prioridad": "NORMAL",
                "estatus": "PLANIFICADA",
                "cliente": "A0009",
                "razon_social": "WALMART",
                "caja": "IGG0138 - CAJA",
                "dimensiones": "QUARRY 40 X 30 X 15",
                "materiales": [
                    {"mp": "HCW0736", "descripcion": "FLEX - WILSON ESTUCHE DAMAS TIN AFELPADO 6 PARES", "cantidad": 1},
                    {"mp": "HGG0476", "descripcion": "GANCHO GOTA AZUL", "cantidad": 1},
                    {"mp": "IGG0046", "descripcion": "PLASTIFLECHA DE 1.5 PULGADA", "cantidad": 1}
                ]
            },
            {
                "of": "523806",
                "pt": "A6955",
                "descripcion": "SIXPAR ESTCHE TIN CB PREM NGPT",
                "upc": "7506424069553",
                "cantidad": 36,
                "pendiente": 36,
                "avance": 0.0,
                "prioridad": "NORMAL",
                "estatus": "PLANIFICADA",
                "cliente": "A0010",
                "razon_social": "COSTCO",
                "caja": "IGG0139 - CAJA",
                "dimensiones": "QUARRY 45 X 35 X 20",
                "materiales": [
                    {"mp": "HCW0737", "descripcion": "FLEX - WILSON ESTUCHE UNISEX TIN AFELPADO 6 PARES", "cantidad": 1},
                    {"mp": "HGG0477", "descripcion": "GANCHO GOTA VERDE", "cantidad": 1}
                ]
            }
        ]

        # Estadísticas globales
        self.total_fabricar = sum(item["cantidad"] for item in self.carga_trabajo)
        self.codigos_pendientes = sum(item["pendiente"] for item in self.carga_trabajo)
        self.avance_global = 0.0

        # Colores del tema
        self.colores = {
            'fondo': '#1a1a2e',
            'panel': '#16213e',
            'texto': '#ffffff',
            'texto_secundario': '#cccccc',
            'accento': '#0f3460',
            'verde': '#00ff00',
            'amarillo': '#ffaa00',
            'rojo': '#ff0000',
            'azul': '#0099ff',
            'borde': '#444444',
            'tabla_fondo': '#0e1621',
            'tabla_header': '#16213e'
        }

        # Fuentes
        self.fuente_titulo = ('Arial', 24, 'bold')
        self.fuente_grande = ('Arial', 18, 'bold')
        self.fuente_normal = ('Arial', 12)
        self.fuente_pequena = ('Arial', 10)

    def crear_interfaz(self):
        """Crear la interfaz principal del dashboard"""
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Monitor Industrial SISPRO - Dashboard")
        self.root.configure(bg=self.colores['fondo'])
        self.root.state('zoomed')  # Maximizar ventana

        # Configurar teclas de salida
        self.root.bind('<Escape>', self.salir)
        self.root.bind('<Command-q>', self.salir)

        # Crear frame principal
        main_frame = tk.Frame(self.root, bg=self.colores['fondo'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear barra superior
        self.crear_barra_superior(main_frame)

        # Crear panel de información de estación
        self.crear_panel_estacion(main_frame)

        # Crear estadísticas globales
        self.crear_estadisticas_globales(main_frame)

        # Crear tabla de carga de trabajo
        self.crear_tabla_carga_trabajo(main_frame)

        # Crear controles inferiores
        self.crear_controles_inferiores(main_frame)

        # Actualizar reloj
        self.actualizar_reloj()

    def crear_barra_superior(self, parent):
        """Crear barra superior con menú y usuario"""
        barra_frame = tk.Frame(parent, bg=self.colores['panel'], height=60)
        barra_frame.pack(fill=tk.X, pady=(0, 10))
        barra_frame.pack_propagate(False)

        # Menú
        menu_btn = tk.Button(
            barra_frame,
            text="☰ Menu",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['accento'],
            relief=tk.FLAT,
            bd=0
        )
        menu_btn.pack(side=tk.LEFT, padx=10, pady=15)

        # Dashboard
        dashboard_btn = tk.Button(
            barra_frame,
            text="📊 Dashboard",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['verde'],
            relief=tk.FLAT,
            bd=0
        )
        dashboard_btn.pack(side=tk.LEFT, padx=10, pady=15)

        # Reloj
        self.reloj_var = tk.StringVar()
        self.reloj_label = tk.Label(
            barra_frame,
            textvariable=self.reloj_var,
            font=('Arial', 16, 'bold'),
            fg=self.colores['texto'],
            bg=self.colores['panel']
        )
        self.reloj_label.pack(side=tk.RIGHT, padx=20, pady=15)

        # Usuario
        usuario_label = tk.Label(
            barra_frame,
            text="ADMINISTRADOR",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        )
        usuario_label.pack(side=tk.RIGHT, padx=10, pady=15)

        # Cerrar sesión
        cerrar_btn = tk.Button(
            barra_frame,
            text="Cerrar sesión →",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['rojo'],
            relief=tk.FLAT,
            bd=0,
            command=self.salir
        )
        cerrar_btn.pack(side=tk.RIGHT, padx=10, pady=15)

    def crear_panel_estacion(self, parent):
        """Crear panel de información de la estación"""
        estacion_frame = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        estacion_frame.pack(fill=tk.X, pady=(0, 10))

        # Título de estación
        titulo_frame = tk.Frame(estacion_frame, bg=self.colores['panel'])
        titulo_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            titulo_frame,
            text=self.estacion_actual['nombre'],
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT)

        # Información de coordinador y cuadrante
        info_frame = tk.Frame(estacion_frame, bg=self.colores['panel'])
        info_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(
            info_frame,
            text=f"👤 {self.estacion_actual['coordinador']}",
            font=self.fuente_normal,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            info_frame,
            text=f"📍 {self.estacion_actual['cuadrante']}",
            font=self.fuente_normal,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT)

        # Última actualización
        actualizacion_label = tk.Label(
            estacion_frame,
            text=f"Última actualización: {self.estacion_actual['ultima_actualizacion']}",
            font=self.fuente_pequena,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        )
        actualizacion_label.pack(padx=20, pady=(0, 10))

    def crear_estadisticas_globales(self, parent):
        """Crear panel de estadísticas globales"""
        stats_frame = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        # Título
        tk.Label(
            stats_frame,
            text="ESTADÍSTICAS GLOBALES",
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(pady=10)

        # Métricas
        metrics_frame = tk.Frame(stats_frame, bg=self.colores['panel'])
        metrics_frame.pack(pady=10)

        # Total a Fabricar
        tk.Label(
            metrics_frame,
            text="Total a Fabricar",
            font=self.fuente_normal,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).grid(row=0, column=0, padx=20, sticky=tk.W)

        tk.Label(
            metrics_frame,
            text=str(self.total_fabricar),
            font=('Arial', 24, 'bold'),
            fg=self.colores['verde'],
            bg=self.colores['panel']
        ).grid(row=1, column=0, padx=20, sticky=tk.W)

        # Códigos Pendientes
        tk.Label(
            metrics_frame,
            text="Códigos Pendientes",
            font=self.fuente_normal,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).grid(row=0, column=1, padx=20, sticky=tk.W)

        tk.Label(
            metrics_frame,
            text=str(self.codigos_pendientes),
            font=('Arial', 24, 'bold'),
            fg=self.colores['amarillo'],
            bg=self.colores['panel']
        ).grid(row=1, column=1, padx=20, sticky=tk.W)

        # Avance Global
        tk.Label(
            metrics_frame,
            text="Avance Global",
            font=self.fuente_normal,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).grid(row=0, column=2, padx=20, sticky=tk.W)

        tk.Label(
            metrics_frame,
            text=f"{self.avance_global:.1f}%",
            font=('Arial', 24, 'bold'),
            fg=self.colores['azul'],
            bg=self.colores['panel']
        ).grid(row=1, column=2, padx=20, sticky=tk.W)

    def crear_tabla_carga_trabajo(self, parent):
        """Crear tabla de carga de trabajo asignada"""
        tabla_frame = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        tabla_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Título y controles
        header_frame = tk.Frame(tabla_frame, bg=self.colores['panel'])
        header_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            header_frame,
            text="CARGA DE TRABAJO ASIGNADA",
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT)

        # Controles de tabla
        controles_frame = tk.Frame(header_frame, bg=self.colores['panel'])
        controles_frame.pack(side=tk.RIGHT)

        tk.Label(
            controles_frame,
            text="Columnas",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=5)

        columnas_combo = ttk.Combobox(controles_frame, values=["Todas", "Básicas", "Completas"])
        columnas_combo.set("Todas")
        columnas_combo.pack(side=tk.LEFT, padx=5)

        # Buscar
        buscar_entry = tk.Entry(controles_frame, width=20)
        buscar_entry.pack(side=tk.LEFT, padx=5)
        buscar_entry.insert(0, "Buscar...")

        # Crear tabla con Treeview
        self.crear_tabla_datos(tabla_frame)

    def crear_tabla_datos(self, parent):
        """Crear la tabla de datos con Treeview"""
        # Frame para la tabla
        tabla_container = tk.Frame(parent, bg=self.colores['panel'])
        tabla_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # Crear Treeview
        columns = ('OF', 'PT', 'Descripción', 'UPC', 'Cantidad', 'Pendiente', 'Avance', 'Prioridad', 'Acciones')
        self.tabla = ttk.Treeview(tabla_container, columns=columns, show='headings', height=10)

        # Configurar columnas
        self.tabla.heading('OF', text='OF')
        self.tabla.heading('PT', text='PT')
        self.tabla.heading('Descripción', text='Descripción')
        self.tabla.heading('UPC', text='UPC')
        self.tabla.heading('Cantidad', text='Cantidad')
        self.tabla.heading('Pendiente', text='Pendiente')
        self.tabla.heading('Avance', text='Avance')
        self.tabla.heading('Prioridad', text='Prioridad')
        self.tabla.heading('Acciones', text='Acciones')

        # Configurar anchos de columnas
        self.tabla.column('OF', width=80)
        self.tabla.column('PT', width=80)
        self.tabla.column('Descripción', width=300)
        self.tabla.column('UPC', width=120)
        self.tabla.column('Cantidad', width=80)
        self.tabla.column('Pendiente', width=80)
        self.tabla.column('Avance', width=80)
        self.tabla.column('Prioridad', width=80)
        self.tabla.column('Acciones', width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_container, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Pack tabla y scrollbar
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Insertar datos
        self.actualizar_tabla_datos()

        # Bind eventos
        self.tabla.bind('<Double-1>', self.abrir_lectura)

    def actualizar_tabla_datos(self):
        """Actualizar datos en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        # Insertar datos
        for item in self.carga_trabajo:
            self.tabla.insert('', 'end', values=(
                item['of'],
                item['pt'],
                item['descripcion'],
                item['upc'],
                item['cantidad'],
                item['pendiente'],
                f"{item['avance']:.1f}%",
                item['prioridad'],
                "Leer UPC | Prioridad"
            ))

    def abrir_lectura(self, event):
        """Abrir pantalla de lectura para el item seleccionado"""
        try:
            selection = self.tabla.selection()
            if not selection:
                return

            item = self.tabla.item(selection[0])
            of = item['values'][0]
            pt = item['values'][1]

            # Buscar el item en la carga de trabajo
            trabajo_item = None
            for item in self.carga_trabajo:
                if item['of'] == of and item['pt'] == pt:
                    trabajo_item = item
                    break

            if trabajo_item:
                self.mostrar_pantalla_lectura(trabajo_item)

        except Exception as e:
            logger.error(f"❌ Error abriendo lectura: {e}")
            messagebox.showerror("Error", f"Error abriendo lectura: {e}")

    def mostrar_pantalla_lectura(self, item):
        """Mostrar pantalla de lectura de PT"""
        # Crear ventana modal
        lectura_window = tk.Toplevel(self.root)
        lectura_window.title(f"LECTURA DE PT: {item['pt']}")
        lectura_window.configure(bg=self.colores['fondo'])
        lectura_window.geometry("1000x700")
        lectura_window.transient(self.root)
        lectura_window.grab_set()

        # Centrar ventana
        lectura_window.update_idletasks()
        x = (lectura_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (lectura_window.winfo_screenheight() // 2) - (700 // 2)
        lectura_window.geometry(f"1000x700+{x}+{y}")

        # Frame principal
        main_frame = tk.Frame(lectura_window, bg=self.colores['fondo'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Título
        titulo_frame = tk.Frame(header_frame, bg=self.colores['panel'])
        titulo_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            titulo_frame,
            text=f"LECTURA DE PT: {item['pt']}",
            font=self.fuente_titulo,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT)

        # Botón cerrar
        cerrar_btn = tk.Button(
            titulo_frame,
            text="✕",
            font=('Arial', 16, 'bold'),
            fg=self.colores['texto'],
            bg=self.colores['rojo'],
            relief=tk.FLAT,
            bd=0,
            command=lectura_window.destroy,
            width=3
        )
        cerrar_btn.pack(side=tk.RIGHT)

        # Descripción
        tk.Label(
            header_frame,
            text=f"DESCRIPCIÓN: {item['descripcion']}",
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(padx=20, pady=(0, 10))

        # Información de la orden
        info_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        info_content = tk.Frame(info_frame, bg=self.colores['panel'])
        info_content.pack(fill=tk.X, padx=20, pady=10)

        # Orden de fabricación
        tk.Label(
            info_content,
            text=f"ORDEN DE FABRICACIÓN: {item['of']}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Estatus
        tk.Label(
            info_content,
            text=f"ESTATUS: {item['estatus']}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Cliente
        tk.Label(
            info_content,
            text=f"CLIENTE: {item['cliente']}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Razón social
        tk.Label(
            info_content,
            text=f"RAZÓN SOCIAL: {item['razon_social']}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Información de caja
        caja_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        caja_frame.pack(fill=tk.X, pady=(0, 20))

        caja_content = tk.Frame(caja_frame, bg=self.colores['panel'])
        caja_content.pack(fill=tk.X, padx=20, pady=10)

        # Caja
        tk.Label(
            caja_content,
            text=f"CAJA: {item['caja']}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Dimensiones
        tk.Label(
            caja_content,
            text=f"{item['dimensiones']}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Tabla de materiales
        materiales_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        materiales_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        tk.Label(
            materiales_frame,
            text="MATERIALES REQUERIDOS",
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(pady=10)

        # Crear tabla de materiales
        materiales_tree = ttk.Treeview(materiales_frame, columns=('MP', 'Descripción', 'Cantidad'), show='headings', height=6)
        materiales_tree.heading('MP', text='MP')
        materiales_tree.heading('Descripción', text='DESCRIPCIÓN MP')
        materiales_tree.heading('Cantidad', text='CANTIDAD')

        materiales_tree.column('MP', width=100)
        materiales_tree.column('Descripción', width=400)
        materiales_tree.column('Cantidad', width=100)

        # Insertar materiales
        for material in item['materiales']:
            materiales_tree.insert('', 'end', values=(
                material['mp'],
                material['descripcion'],
                material['cantidad']
            ))

        materiales_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # Estadísticas de la tarea
        stats_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        stats_content = tk.Frame(stats_frame, bg=self.colores['panel'])
        stats_content.pack(fill=tk.X, padx=20, pady=10)

        # Métricas
        metrics_frame = tk.Frame(stats_content, bg=self.colores['panel'])
        metrics_frame.pack(fill=tk.X)

        tk.Label(
            metrics_frame,
            text=f"FABRICAR: {item['cantidad']}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            metrics_frame,
            text=f"PENDIENTE: {item['pendiente']}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            metrics_frame,
            text=f"AVANCE: {item['avance']:.1f}%",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            metrics_frame,
            text="CAJAS: 0",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=20)

        # Sección de escaneo UPC
        upc_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        upc_frame.pack(fill=tk.X, pady=(0, 20))

        upc_content = tk.Frame(upc_frame, bg=self.colores['panel'])
        upc_content.pack(fill=tk.X, padx=20, pady=10)

        # Escanear UPC
        tk.Label(
            upc_content,
            text="Escanear UPC",
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W, pady=(0, 5))

        # Campo de entrada UPC
        upc_entry = tk.Entry(upc_content, font=self.fuente_normal, width=30)
        upc_entry.pack(anchor=tk.W, pady=(0, 5))
        upc_entry.focus()

        # UPC esperado
        tk.Label(
            upc_content,
            text=f"UPC esperado: {item['upc']}",
            font=self.fuente_normal,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Función para validar UPC
        def validar_upc(event=None):
            upc_ingresado = upc_entry.get().strip()
            if upc_ingresado == item['upc']:
                messagebox.showinfo("Éxito", "UPC válido. Iniciando producción...")
                self.iniciar_produccion(item)
                lectura_window.destroy()
            else:
                messagebox.showerror("Error", "UPC inválido. Verifique el código.")
                upc_entry.delete(0, tk.END)

        upc_entry.bind('<Return>', validar_upc)

        # Botón cerrar lectura
        cerrar_lectura_btn = tk.Button(
            main_frame,
            text="✕ Cerrar Lectura",
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['borde'],
            relief=tk.RAISED,
            bd=2,
            command=lectura_window.destroy,
            width=20,
            height=2
        )
        cerrar_lectura_btn.pack(pady=10)

    def iniciar_produccion(self, item):
        """Iniciar producción del item seleccionado"""
        try:
            # Actualizar estado del item
            item['estatus'] = 'EN PRODUCCIÓN'
            item['avance'] = 0.0

            # Iniciar simulación de producción
            self.simular_produccion(item)

            logger.info(f"✅ Producción iniciada para {item['pt']}")
            messagebox.showinfo("Éxito", f"Producción iniciada para {item['pt']}")

        except Exception as e:
            logger.error(f"❌ Error iniciando producción: {e}")
            messagebox.showerror("Error", f"Error iniciando producción: {e}")

    def simular_produccion(self, item):
        """Simular producción del item"""
        def producir():
            while self.running and item['pendiente'] > 0:
                try:
                    # Simular incremento de producción
                    if random.random() < 0.3:  # 30% de probabilidad cada segundo
                        incremento = random.randint(1, 3)
                        item['pendiente'] = max(0, item['pendiente'] - incremento)
                        item['avance'] = ((item['cantidad'] - item['pendiente']) / item['cantidad']) * 100

                        # Actualizar estadísticas globales
                        self.actualizar_estadisticas_globales()

                        # Actualizar tabla
                        self.actualizar_tabla_datos()

                        logger.info(f"📊 Producción {item['pt']}: {item['cantidad'] - item['pendiente']}/{item['cantidad']} ({item['avance']:.1f}%)")

                    time.sleep(1)
                except Exception as e:
                    logger.error(f"❌ Error en simulación: {e}")
                    time.sleep(1)

        self.running = True
        thread = threading.Thread(target=producir, daemon=True)
        thread.start()

    def actualizar_estadisticas_globales(self):
        """Actualizar estadísticas globales"""
        self.codigos_pendientes = sum(item['pendiente'] for item in self.carga_trabajo)
        total_producido = sum(item['cantidad'] - item['pendiente'] for item in self.carga_trabajo)
        self.avance_global = (total_producido / self.total_fabricar) * 100 if self.total_fabricar > 0 else 0

    def crear_controles_inferiores(self, parent):
        """Crear controles inferiores"""
        controles_frame = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        controles_frame.pack(fill=tk.X, pady=(0, 10))

        controles_content = tk.Frame(controles_frame, bg=self.colores['panel'])
        controles_content.pack(fill=tk.X, padx=20, pady=10)

        # Botón de asistencia
        asistencia_btn = tk.Button(
            controles_content,
            text="🆘 Centro de asistencia",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['verde'],
            relief=tk.RAISED,
            bd=2
        )
        asistencia_btn.pack(side=tk.LEFT, padx=10)

        # Mostrar órdenes cerradas
        tk.Label(
            controles_content,
            text="Mostrar órdenes cerradas",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=20)

        cerradas_var = tk.BooleanVar()
        cerradas_check = tk.Checkbutton(
            controles_content,
            variable=cerradas_var,
            bg=self.colores['panel'],
            fg=self.colores['texto']
        )
        cerradas_check.pack(side=tk.LEFT, padx=5)

        # Botón CSV
        csv_btn = tk.Button(
            controles_content,
            text="📊 CSV",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['azul'],
            relief=tk.RAISED,
            bd=2
        )
        csv_btn.pack(side=tk.RIGHT, padx=10)

        # Paginación
        paginacion_frame = tk.Frame(controles_content, bg=self.colores['panel'])
        paginacion_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(
            paginacion_frame,
            text="Filas por página 10",
            font=self.fuente_pequena,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(
            paginacion_frame,
            text="1-10 de 30",
            font=self.fuente_pequena,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=5)

    def actualizar_reloj(self):
        """Actualizar reloj en tiempo real"""
        try:
            ahora = datetime.now()
            tiempo_str = ahora.strftime("%H:%M:%S")
            self.reloj_var.set(tiempo_str)
            self.root.after(1000, self.actualizar_reloj)
        except Exception as e:
            logger.error(f"❌ Error actualizando reloj: {e}")

    def salir(self, event=None):
        """Salir de la aplicación"""
        try:
            if messagebox.askyesno("Confirmar", "¿Salir del Monitor Industrial?"):
                self.running = False
                self.root.quit()
        except Exception as e:
            logger.error(f"❌ Error saliendo: {e}")
            self.root.quit()

    def ejecutar(self):
        """Ejecutar el monitor"""
        try:
            print("🍓 Monitor Industrial SISPRO - Dashboard")
            print("=" * 50)
            print("Dashboard con carga de trabajo asignada")
            print("Haga doble clic en cualquier fila para abrir la pantalla de lectura")
            print("=" * 50)
            print()

            self.crear_interfaz()
            logger.info("✅ Dashboard creado")
            self.root.mainloop()

        except Exception as e:
            logger.error(f"❌ Error en ejecución: {e}")
            print(f"❌ Error fatal: {e}")

def main():
    """Función principal"""
    monitor = MonitorIndustrialDashboard()
    monitor.ejecutar()

if __name__ == "__main__":
    main()
