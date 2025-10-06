#!/usr/bin/env python3
"""
Interfaz Industrial Fullscreen - Monitor de Estación de Trabajo
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

class InterfazIndustrial:
    def __init__(self, monitor):
        self.monitor = monitor
        self.root = None
        self.logger = logging.getLogger(__name__)

        # Variables de la interfaz
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
            self.configurar_ventana()
            self.crear_interfaz()
            self.iniciar_actualizaciones()
            self.logger.info("✅ Interfaz industrial mostrada")
        except Exception as e:
            self.logger.error(f"❌ Error mostrando interfaz: {e}")

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
            self.logger.error(f"❌ Error configurando ventana: {e}")

    def crear_interfaz(self):
        """Crear interfaz principal"""
        try:
            # Frame principal
            main_frame = tk.Frame(self.root, bg=self.colores['fondo'])
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Crear paneles
            self.crear_panel_superior(main_frame)
            self.crear_panel_central(main_frame)
            self.crear_panel_inferior(main_frame)
            self.crear_panel_estado(main_frame)

        except Exception as e:
            self.logger.error(f"❌ Error creando interfaz: {e}")

    def crear_panel_superior(self, parent):
        """Crear panel superior con información de la estación"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X, pady=(0, 10))

            # Título principal
            titulo = tk.Label(
                panel,
                text="🍓 MONITOR INDUSTRIAL SISPRO",
                font=self.fuente_titulo,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            )
            titulo.pack(pady=10)

            # Información de la estación
            info_frame = tk.Frame(panel, bg=self.colores['panel'])
            info_frame.pack(pady=10)

            # Estación
            tk.Label(
                info_frame,
                text="Estación:",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=0, padx=10, sticky=tk.W)

            tk.Label(
                info_frame,
                textvariable=self.estacion_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=1, padx=10, sticky=tk.W)

            # Estado
            tk.Label(
                info_frame,
                text="Estado:",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=2, padx=10, sticky=tk.W)

            tk.Label(
                info_frame,
                textvariable=self.estado_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=3, padx=10, sticky=tk.W)

        except Exception as e:
            self.logger.error(f"❌ Error creando panel superior: {e}")

    def crear_panel_central(self, parent):
        """Crear panel central con información de producción"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # Información de la orden
            orden_frame = tk.Frame(panel, bg=self.colores['panel'])
            orden_frame.pack(fill=tk.X, pady=20)

            # Orden de fabricación
            tk.Label(
                orden_frame,
                text="Orden:",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=0, padx=20, sticky=tk.W)

            tk.Label(
                orden_frame,
                textvariable=self.orden_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=1, padx=20, sticky=tk.W)

            # UPC
            tk.Label(
                orden_frame,
                text="UPC:",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=2, padx=20, sticky=tk.W)

            tk.Label(
                orden_frame,
                textvariable=self.upc_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=3, padx=20, sticky=tk.W)

            # Contador principal
            contador_frame = tk.Frame(panel, bg=self.colores['panel'])
            contador_frame.pack(expand=True)

            # Contador actual
            tk.Label(
                contador_frame,
                text="CONTADOR",
                font=self.fuente_grande,
                fg=self.colores['texto_secundario'],
                bg=self.colores['panel']
            ).pack()

            tk.Label(
                contador_frame,
                textvariable=self.contador_var,
                font=('Arial', 48, 'bold'),
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).pack(pady=10)

            # Meta y progreso
            meta_frame = tk.Frame(panel, bg=self.colores['panel'])
            meta_frame.pack(pady=20)

            # Meta
            tk.Label(
                meta_frame,
                text="META:",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=0, padx=20, sticky=tk.W)

            tk.Label(
                meta_frame,
                textvariable=self.meta_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=1, padx=20, sticky=tk.W)

            # Progreso
            tk.Label(
                meta_frame,
                text="PROGRESO:",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=2, padx=20, sticky=tk.W)

            tk.Label(
                meta_frame,
                textvariable=self.progreso_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=3, padx=20, sticky=tk.W)

            # Barra de progreso
            self.progreso_barra = ttk.Progressbar(
                panel,
                length=600,
                mode='determinate',
                style='Industrial.Horizontal.TProgressbar'
            )
            self.progreso_barra.pack(pady=20)

            # Configurar estilo de la barra de progreso
            self.configurar_estilo_progreso()

        except Exception as e:
            self.logger.error(f"❌ Error creando panel central: {e}")

    def crear_panel_inferior(self, parent):
        """Crear panel inferior con botones de control"""
        try:
            panel = tk.Frame(parent, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            panel.pack(fill=tk.X, pady=(0, 10))

            # Botones de control
            botones_frame = tk.Frame(panel, bg=self.colores['panel'])
            botones_frame.pack(pady=20)

            # Botón seleccionar estación
            btn_estacion = tk.Button(
                botones_frame,
                text="🏭 SELECCIONAR ESTACIÓN",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['borde'],
                relief=tk.RAISED,
                bd=3,
                command=self.seleccionar_estacion,
                width=20,
                height=2
            )
            btn_estacion.grid(row=0, column=0, padx=10, pady=5)

            # Botón seleccionar orden
            btn_orden = tk.Button(
                botones_frame,
                text="📦 SELECCIONAR ORDEN",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['borde'],
                relief=tk.RAISED,
                bd=3,
                command=self.seleccionar_orden,
                width=20,
                height=2
            )
            btn_orden.grid(row=0, column=1, padx=10, pady=5)

            # Botón validar UPC
            btn_upc = tk.Button(
                botones_frame,
                text="📱 VALIDAR UPC",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['borde'],
                relief=tk.RAISED,
                bd=3,
                command=self.validar_upc,
                width=20,
                height=2
            )
            btn_upc.grid(row=0, column=2, padx=10, pady=5)

            # Botón finalizar orden
            btn_finalizar = tk.Button(
                botones_frame,
                text="✅ FINALIZAR ORDEN",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                relief=tk.RAISED,
                bd=3,
                command=self.finalizar_orden,
                width=20,
                height=2
            )
            btn_finalizar.grid(row=1, column=0, padx=10, pady=5)

            # Botón sincronizar
            btn_sincronizar = tk.Button(
                botones_frame,
                text="🔄 SINCRONIZAR",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['info'],
                relief=tk.RAISED,
                bd=3,
                command=self.sincronizar_ahora,
                width=20,
                height=2
            )
            btn_sincronizar.grid(row=1, column=1, padx=10, pady=5)

            # Botón salir
            btn_salir = tk.Button(
                botones_frame,
                text="🚪 SALIR",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['error'],
                relief=tk.RAISED,
                bd=3,
                command=self.salir,
                width=20,
                height=2
            )
            btn_salir.grid(row=1, column=2, padx=10, pady=5)

        except Exception as e:
            self.logger.error(f"❌ Error creando panel inferior: {e}")

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

        except Exception as e:
            self.logger.error(f"❌ Error creando panel de estado: {e}")

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
            self.logger.error(f"❌ Error configurando estilo progreso: {e}")

    def iniciar_actualizaciones(self):
        """Iniciar actualizaciones automáticas de la interfaz"""
        try:
            self.actualizar_interfaz()
            self.root.after(self.monitor.config.update_interval, self.iniciar_actualizaciones)
        except Exception as e:
            self.logger.error(f"❌ Error en actualizaciones: {e}")

    def actualizar_interfaz(self):
        """Actualizar elementos de la interfaz"""
        try:
            # Actualizar estado del sistema
            self.estado_var.set(self.monitor.estado.estado_actual.value)

            # Actualizar información de la estación
            if self.monitor.estacion_actual:
                self.estacion_var.set(self.monitor.estacion_actual.get('nombre', 'N/A'))

            # Actualizar información de la orden
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

            # Actualizar contador
            self.contador_var.set(str(self.monitor.lecturas_acumuladas))

            # Actualizar última sincronización
            if self.monitor.ultima_sincronizacion:
                self.ultima_sincronizacion_var.set(
                    self.monitor.ultima_sincronizacion.strftime("%H:%M:%S")
                )

        except Exception as e:
            self.logger.error(f"❌ Error actualizando interfaz: {e}")

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
            self.logger.error(f"❌ Error actualizando contador: {e}")

    def actualizar_avance(self, avance: Dict[str, Any]):
        """Actualizar avance de la orden"""
        try:
            if avance:
                cantidad_pendiente = avance.get('cantidadPendiente', 0)
                avance_porcentaje = avance.get('avance', 0) * 100

                self.progreso_var.set(f"{avance_porcentaje:.1f}%")
                self.progreso_barra['value'] = avance_porcentaje

        except Exception as e:
            self.logger.error(f"❌ Error actualizando avance: {e}")

    def actualizar_estado_pico(self, estado: Dict[str, Any]):
        """Actualizar estado del Pico"""
        try:
            if estado:
                self.estado_pico_var.set(estado.get('estado', 'DESCONECTADO'))
                self.tiempo_inactivo_var.set(f"{estado.get('tiempo_inactivo', 0)}s")

        except Exception as e:
            self.logger.error(f"❌ Error actualizando estado Pico: {e}")

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

            # Título
            tk.Label(
                frame,
                text="SELECCIONAR ESTACIÓN DE TRABAJO",
                font=self.fuente_titulo,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=20)

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
            self.logger.error(f"❌ Error mostrando selección de estación: {e}")
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

            # Título
            tk.Label(
                frame,
                text="SELECCIONAR ORDEN DE FABRICACIÓN",
                font=self.fuente_titulo,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=20)

            # Lista de órdenes
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

            # Agregar órdenes a la lista
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
            self.logger.error(f"❌ Error mostrando selección de orden: {e}")
            return None

    def seleccionar_estacion(self):
        """Seleccionar estación de trabajo"""
        try:
            self.monitor.seleccionar_estacion()
        except Exception as e:
            self.logger.error(f"❌ Error seleccionando estación: {e}")
            messagebox.showerror("Error", f"Error seleccionando estación: {e}")

    def seleccionar_orden(self):
        """Seleccionar orden de fabricación"""
        try:
            self.monitor.seleccionar_orden()
        except Exception as e:
            self.logger.error(f"❌ Error seleccionando orden: {e}")
            messagebox.showerror("Error", f"Error seleccionando orden: {e}")

    def validar_upc(self):
        """Validar código UPC"""
        try:
            upc = simpledialog.askstring(
                "Validar UPC",
                "Ingrese el código UPC:",
                parent=self.root
            )

            if upc:
                if self.monitor.validar_upc(upc):
                    messagebox.showinfo("Éxito", "UPC válido. Producción iniciada.")
                else:
                    messagebox.showerror("Error", "UPC inválido. Verifique el código.")

        except Exception as e:
            self.logger.error(f"❌ Error validando UPC: {e}")
            messagebox.showerror("Error", f"Error validando UPC: {e}")

    def finalizar_orden(self):
        """Finalizar orden actual"""
        try:
            if messagebox.askyesno("Confirmar", "¿Finalizar la orden actual?"):
                self.monitor.finalizar_orden()
                messagebox.showinfo("Éxito", "Orden finalizada correctamente.")
        except Exception as e:
            self.logger.error(f"❌ Error finalizando orden: {e}")
            messagebox.showerror("Error", f"Error finalizando orden: {e}")

    def sincronizar_ahora(self):
        """Sincronizar datos ahora"""
        try:
            self.monitor.sincronizar_lecturas()
            messagebox.showinfo("Éxito", "Datos sincronizados correctamente.")
        except Exception as e:
            self.logger.error(f"❌ Error sincronizando: {e}")
            messagebox.showerror("Error", f"Error sincronizando: {e}")

    def toggle_fullscreen(self, event=None):
        """Alternar modo fullscreen"""
        try:
            self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        except Exception as e:
            self.logger.error(f"❌ Error alternando fullscreen: {e}")

    def salir(self, event=None):
        """Salir de la aplicación"""
        try:
            if messagebox.askyesno("Confirmar", "¿Salir del Monitor Industrial?"):
                self.monitor.detener()
                self.root.quit()
        except Exception as e:
            self.logger.error(f"❌ Error saliendo: {e}")
            self.root.quit()
