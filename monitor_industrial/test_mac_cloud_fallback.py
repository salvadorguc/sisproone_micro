#!/usr/bin/env python3
"""
Monitor Industrial SISPRO - Con Fallback a Datos Simulados
Versión que intenta conectar a la nube pero usa datos simulados si falla
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import random
import logging
import requests
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonitorIndustrialCloudFallback:
    def __init__(self):
        # Estado del sistema
        self.estacion_actual = None
        self.orden_actual = None
        self.upc_validado = None
        self.lecturas_acumuladas = 0
        self.running = False
        self.token = None
        self.conectado_cloud = False

        # Configuración de la nube
        self.base_url = "http://100.24.193.207:3000"
        self.username = "MONITORPI"
        self.password = "56fg453drJ"
        self.empresa_id = 1
        self.usuario_id = 1

        # Datos simulados como fallback
        self.estaciones_simuladas = [
            {
                "id": 10,
                "nombre": "ESTACION 10",
                "descripcion": "Estación de Prueba",
                "coordinador": "Juan Pérez",
                "cuadrante": "Cuadrante A",
                "estado": "ASIGNADA"
            },
            {
                "id": 11,
                "nombre": "ESTACION 11",
                "descripcion": "Estación de Prueba 2",
                "coordinador": "María García",
                "cuadrante": "Cuadrante B",
                "estado": "ASIGNADA"
            }
        ]

        self.carga_trabajo_simulada = [
            {
                "ordenFabricacion": "523804",
                "pt": "A6953",
                "ptDescripcion": "P6ME TIN CAB PREMIUM OXFORD",
                "ptUPC": "7506424069539",
                "cantidadFabricar": 48,
                "cantidadPendiente": 48,
                "avance": 0.0,
                "prioridad": "NORMAL",
                "estatus": "PLANIFICADA",
                "cliente": "A0008",
                "razonSocial": "TIENDAS SORIANA"
            },
            {
                "ordenFabricacion": "523805",
                "pt": "A6954",
                "ptDescripcion": "BOLSA C/6 DAM JASPE UNI",
                "ptUPC": "7506424069546",
                "cantidadFabricar": 24,
                "cantidadPendiente": 24,
                "avance": 0.0,
                "prioridad": "NORMAL",
                "estatus": "PLANIFICADA",
                "cliente": "A0009",
                "razonSocial": "WALMART"
            },
            {
                "ordenFabricacion": "523806",
                "pt": "A6955",
                "ptDescripcion": "SIXPAR ESTCHE TIN CB PREM NGPT",
                "ptUPC": "7506424069553",
                "cantidadFabricar": 36,
                "cantidadPendiente": 36,
                "avance": 0.0,
                "prioridad": "NORMAL",
                "estatus": "PLANIFICADA",
                "cliente": "A0010",
                "razonSocial": "COSTCO"
            }
        ]

        # Datos de la nube
        self.estaciones = []
        self.carga_trabajo = []
        self.total_fabricar = 0
        self.codigos_pendientes = 0
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

    def autenticar(self):
        """Autenticar con el sistema SISPRO usando middleware de autenticación"""
        try:
            url = f"{self.base_url}/api/auth/login"
            headers = {'Content-Type': 'application/json'}
            payload = {
                'username': self.username,
                'password': self.password
            }

            response = requests.post(url, headers=headers, json=payload, timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.conectado_cloud = True
                logger.info("✅ Autenticación exitosa con SISPRO")
                logger.info(f"🔐 Token obtenido: {self.token[:20]}...")
                logger.info(f"🏢 Empresa ID: {self.empresa_id}")
                return True
            else:
                logger.warning(f"⚠️ Error de autenticación: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.warning(f"⚠️ No se pudo conectar a SISPRO: {e}")
            return False

    def obtener_estaciones(self):
        """Obtener estaciones de trabajo desde SISPRO o usar simuladas"""
        if not self.conectado_cloud:
            logger.info("📡 Usando datos simulados para estaciones")
            self.estaciones = self.estaciones_simuladas
            return True

        try:
            url = f"{self.base_url}/api/estacionesTrabajo"
            headers = {
                'empresa-id': str(self.empresa_id),  # Siempre usar empresa-id 1
                'Authorization': f'Bearer {self.token}'
            }

            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    self.estaciones = data.get('data', [])
                    logger.info(f"✅ Obtenidas {len(self.estaciones)} estaciones desde SISPRO")
                    return True
                else:
                    logger.warning(f"⚠️ Respuesta SISPRO no exitosa, usando simuladas")
                    self.estaciones = self.estaciones_simuladas
                    return True
            else:
                logger.warning(f"⚠️ Error obteniendo estaciones ({response.status_code}), usando simuladas")
                self.estaciones = self.estaciones_simuladas
                return True

        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo estaciones, usando simuladas: {e}")
            self.estaciones = self.estaciones_simuladas
            return True

    def obtener_carga_trabajo(self, estacion_id):
        """Obtener carga de trabajo asignada desde SISPRO o usar simulada"""
        if not self.conectado_cloud:
            logger.info("📡 Usando datos simulados para carga de trabajo")
            self.carga_trabajo = self.carga_trabajo_simulada
            self.calcular_estadisticas()
            return True

        try:
            url = f"{self.base_url}/api/ordenesDeFabricacion/listarAsignadas"
            headers = {
                'empresa-id': str(self.empresa_id),  # Siempre usar empresa-id 1
                'Authorization': f'Bearer {self.token}'
            }
            params = {'estacionTrabajoId': estacion_id}

            response = requests.get(url, headers=headers, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    self.carga_trabajo = data.get('data', [])
                    logger.info(f"✅ Obtenida carga de trabajo desde SISPRO: {len(self.carga_trabajo)} órdenes")
                else:
                    logger.warning(f"⚠️ Respuesta SISPRO no exitosa, usando simulada")
                    self.carga_trabajo = self.carga_trabajo_simulada
            else:
                logger.warning(f"⚠️ Error obteniendo carga de trabajo ({response.status_code}), usando simulada")
                self.carga_trabajo = self.carga_trabajo_simulada

            self.calcular_estadisticas()
            return True

        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo carga de trabajo, usando simulada: {e}")
            self.carga_trabajo = self.carga_trabajo_simulada
            self.calcular_estadisticas()
            return True

    def calcular_estadisticas(self):
        """Calcular estadísticas globales"""
        self.total_fabricar = sum(item.get('cantidadFabricar', 0) for item in self.carga_trabajo)
        self.codigos_pendientes = sum(item.get('cantidadPendiente', 0) for item in self.carga_trabajo)

        # Calcular avance global
        total_producido = sum(item.get('cantidadFabricar', 0) - item.get('cantidadPendiente', 0) for item in self.carga_trabajo)
        self.avance_global = (total_producido / self.total_fabricar) * 100 if self.total_fabricar > 0 else 0

    def registrar_lectura_upc(self, orden_fabricacion, upc, estacion_id, cantidad=1):
        """Registrar lectura UPC en SISPRO o simular"""
        if not self.conectado_cloud:
            logger.info(f"📡 Simulando registro de lectura UPC: {upc}")
            return True

        try:
            url = f"{self.base_url}/api/lecturaUPC/registrar"
            headers = {
                'empresa-id': str(self.empresa_id),  # Siempre usar empresa-id 1
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'ordenFabricacion': orden_fabricacion,
                'upc': upc,
                'estacionId': estacion_id,
                'usuarioId': self.usuario_id,
                'cantidad': cantidad,
                'timestamp': datetime.now().isoformat(),
                'fuente': 'BARCODE'
            }

            response = requests.post(url, headers=headers, json=payload, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    logger.info(f"✅ Lectura UPC registrada en SISPRO: {upc}")
                    return True
                else:
                    logger.warning(f"⚠️ Respuesta SISPRO no exitosa: {data.get('message', 'Error desconocido')}")
                    return True
            else:
                logger.warning(f"⚠️ Error registrando lectura ({response.status_code}), simulando")
                return True

        except Exception as e:
            logger.warning(f"⚠️ Error registrando lectura, simulando: {e}")
            return True

    def consultar_avance_orden(self, orden_fabricacion):
        """Consultar avance de orden en SISPRO"""
        if not self.conectado_cloud:
            logger.info(f"📡 Simulando consulta de avance para orden: {orden_fabricacion}")
            return {"cantidadPendiente": 0, "avance": 100.0}

        try:
            url = f"{self.base_url}/api/ordenesDeFabricacion/avance"
            headers = {
                'empresa-id': str(self.empresa_id),  # Siempre usar empresa-id 1
                'Authorization': f'Bearer {self.token}'
            }
            params = {'ordenFabricacion': orden_fabricacion}

            response = requests.get(url, headers=headers, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    avance_data = data.get('data', {})
                    logger.info(f"✅ Avance consultado para {orden_fabricacion}: {avance_data}")
                    return avance_data
                else:
                    logger.warning(f"⚠️ Respuesta SISPRO no exitosa para avance")
                    return {"cantidadPendiente": 0, "avance": 0.0}
            else:
                logger.warning(f"⚠️ Error consultando avance ({response.status_code})")
                return {"cantidadPendiente": 0, "avance": 0.0}

        except Exception as e:
            logger.warning(f"⚠️ Error consultando avance, simulando: {e}")
            return {"cantidadPendiente": 0, "avance": 0.0}

    def crear_interfaz(self):
        """Crear la interfaz principal del dashboard"""
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Monitor Industrial SISPRO - Con Fallback")
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

        # Crear panel de selección de estación
        self.crear_panel_seleccion_estacion(main_frame)

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

        # Estado de conexión
        self.estado_conexion_var = tk.StringVar()
        self.estado_conexion_label = tk.Label(
            barra_frame,
            textvariable=self.estado_conexion_var,
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        )
        self.estado_conexion_label.pack(side=tk.LEFT, padx=20, pady=15)

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

    def crear_panel_seleccion_estacion(self, parent):
        """Crear panel de selección de estación"""
        estacion_frame = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        estacion_frame.pack(fill=tk.X, pady=(0, 10))

        # Título
        tk.Label(
            estacion_frame,
            text="SELECCIONAR ESTACIÓN DE TRABAJO",
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(pady=10)

        # Frame para estaciones
        estaciones_frame = tk.Frame(estacion_frame, bg=self.colores['panel'])
        estaciones_frame.pack(fill=tk.X, padx=20, pady=10)

        # Lista de estaciones
        self.estaciones_listbox = tk.Listbox(
            estaciones_frame,
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['tabla_fondo'],
            selectbackground=self.colores['accento'],
            height=4
        )
        self.estaciones_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Botón seleccionar
        seleccionar_btn = tk.Button(
            estaciones_frame,
            text="SELECCIONAR ESTACIÓN",
            font=self.fuente_grande,
            fg=self.colores['texto'],
            bg=self.colores['verde'],
            relief=tk.RAISED,
            bd=2,
            command=self.seleccionar_estacion,
            width=20,
            height=2
        )
        seleccionar_btn.pack(side=tk.RIGHT, padx=10)

        # Cargar estaciones
        self.cargar_estaciones()

    def cargar_estaciones(self):
        """Cargar estaciones desde SISPRO o simuladas"""
        try:
            if self.obtener_estaciones():
                self.estaciones_listbox.delete(0, tk.END)
                for estacion in self.estaciones:
                    texto = f"{estacion.get('nombre', 'N/A')} - {estacion.get('descripcion', 'N/A')}"
                    self.estaciones_listbox.insert(tk.END, texto)

                if self.conectado_cloud:
                    self.estado_conexion_var.set("✅ Conectado a SISPRO")
                else:
                    self.estado_conexion_var.set("📡 Modo Simulación")
            else:
                self.estado_conexion_var.set("❌ Error de conexión")
                messagebox.showerror("Error", "No se pudieron cargar las estaciones")
        except Exception as e:
            logger.error(f"❌ Error cargando estaciones: {e}")
            self.estado_conexion_var.set("❌ Error de conexión")

    def seleccionar_estacion(self):
        """Seleccionar estación de trabajo"""
        try:
            selection = self.estaciones_listbox.curselection()
            if not selection:
                messagebox.showwarning("Advertencia", "Seleccione una estación")
                return

            estacion = self.estaciones[selection[0]]
            self.estacion_actual = estacion

            # Cargar carga de trabajo
            if self.obtener_carga_trabajo(estacion['id']):
                self.actualizar_tabla_datos()
                self.actualizar_estadisticas_globales()
                messagebox.showinfo("Éxito", f"Estación seleccionada: {estacion['nombre']}")
            else:
                messagebox.showerror("Error", "No se pudo cargar la carga de trabajo")

        except Exception as e:
            logger.error(f"❌ Error seleccionando estación: {e}")
            messagebox.showerror("Error", f"Error seleccionando estación: {e}")

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

        self.total_fabricar_var = tk.StringVar(value="0")
        tk.Label(
            metrics_frame,
            textvariable=self.total_fabricar_var,
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

        self.codigos_pendientes_var = tk.StringVar(value="0")
        tk.Label(
            metrics_frame,
            textvariable=self.codigos_pendientes_var,
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

        self.avance_global_var = tk.StringVar(value="0.0%")
        tk.Label(
            metrics_frame,
            textvariable=self.avance_global_var,
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
                item.get('ordenFabricacion', 'N/A'),
                item.get('pt', 'N/A'),
                item.get('ptDescripcion', 'N/A'),
                item.get('ptUPC', 'N/A'),
                item.get('cantidadFabricar', 0),
                item.get('cantidadPendiente', 0),
                f"{item.get('avance', 0):.1f}%",
                item.get('prioridad', 'NORMAL'),
                "Leer UPC | Prioridad"
            ))

    def actualizar_estadisticas_globales(self):
        """Actualizar estadísticas globales en la interfaz"""
        self.total_fabricar_var.set(str(self.total_fabricar))
        self.codigos_pendientes_var.set(str(self.codigos_pendientes))
        self.avance_global_var.set(f"{self.avance_global:.1f}%")

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
                if item.get('ordenFabricacion') == of and item.get('pt') == pt:
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
        lectura_window.title(f"LECTURA DE PT: {item.get('pt', 'N/A')}")
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
            text=f"LECTURA DE PT: {item.get('pt', 'N/A')}",
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
            text=f"DESCRIPCIÓN: {item.get('ptDescripcion', 'N/A')}",
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
            text=f"ORDEN DE FABRICACIÓN: {item.get('ordenFabricacion', 'N/A')}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Estatus
        tk.Label(
            info_content,
            text=f"ESTATUS: {item.get('estatus', 'N/A')}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Cliente
        tk.Label(
            info_content,
            text=f"CLIENTE: {item.get('cliente', 'N/A')}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Razón social
        tk.Label(
            info_content,
            text=f"RAZÓN SOCIAL: {item.get('razonSocial', 'N/A')}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

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
            text=f"FABRICAR: {item.get('cantidadFabricar', 0)}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            metrics_frame,
            text=f"PENDIENTE: {item.get('cantidadPendiente', 0)}",
            font=self.fuente_normal,
            fg=self.colores['texto'],
            bg=self.colores['panel']
        ).pack(side=tk.LEFT, padx=20)

        tk.Label(
            metrics_frame,
            text=f"AVANCE: {item.get('avance', 0):.1f}%",
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
            text=f"UPC esperado: {item.get('ptUPC', 'N/A')}",
            font=self.fuente_normal,
            fg=self.colores['texto_secundario'],
            bg=self.colores['panel']
        ).pack(anchor=tk.W)

        # Función para validar UPC
        def validar_upc(event=None):
            upc_ingresado = upc_entry.get().strip()
            if upc_ingresado == item.get('ptUPC', ''):
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
            # Registrar lectura UPC en SISPRO o simular
            if self.registrar_lectura_upc(
                item.get('ordenFabricacion', ''),
                item.get('ptUPC', ''),
                self.estacion_actual['id'],
                1
            ):
                # Actualizar carga de trabajo
                self.obtener_carga_trabajo(self.estacion_actual['id'])
                self.actualizar_tabla_datos()
                self.actualizar_estadisticas_globales()

                logger.info(f"✅ Producción iniciada para {item.get('pt', 'N/A')}")
                messagebox.showinfo("Éxito", f"Producción iniciada para {item.get('pt', 'N/A')}")
            else:
                messagebox.showerror("Error", "No se pudo registrar la lectura")

        except Exception as e:
            logger.error(f"❌ Error iniciando producción: {e}")
            messagebox.showerror("Error", f"Error iniciando producción: {e}")

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
            print("🍓 Monitor Industrial SISPRO - Con Fallback")
            print("=" * 60)
            print(f"🌐 URL SISPRO: {self.base_url}")
            print(f"👤 Usuario: {self.username}")
            print(f"🏢 Empresa ID: {self.empresa_id}")
            print("=" * 60)
            print()

            # Intentar autenticar con SISPRO
            print("🔐 Intentando autenticar con SISPRO...")
            if self.autenticar():
                print("✅ Conectado a SISPRO - Usando datos reales")
            else:
                print("📡 Modo simulación - Usando datos simulados")
            print()

            self.crear_interfaz()
            logger.info("✅ Dashboard creado")
            self.root.mainloop()

        except Exception as e:
            logger.error(f"❌ Error en ejecución: {e}")
            print(f"❌ Error fatal: {e}")

def main():
    """Función principal"""
    monitor = MonitorIndustrialCloudFallback()
    monitor.ejecutar()

if __name__ == "__main__":
    main()
