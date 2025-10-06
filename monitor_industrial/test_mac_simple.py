#!/usr/bin/env python3
"""
Monitor Industrial SISPRO - Versión Simple para Mac
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import random
import os
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitorIndustrialMac:
    def __init__(self):
        self.root = None
        self.running = False

        # Estado del sistema
        self.estacion_actual = None
        self.orden_actual = None
        self.upc_validado = None
        self.lecturas_acumuladas = 0
        self.contador_var = tk.StringVar(value="0")
        self.meta_var = tk.StringVar(value="0")
        self.progreso_var = tk.StringVar(value="0%")
        self.estado_var = tk.StringVar(value="INACTIVO")
        self.orden_var = tk.StringVar(value="N/A")
        self.upc_var = tk.StringVar(value="N/A")
        self.estacion_var = tk.StringVar(value="N/A")

        # Datos de prueba
        self.estaciones = [
            {
                "id": 1,
                "nombre": "Estación 001",
                "descripcion": "Estación de Prueba",
                "coordinador": "Juan Pérez",
                "cuadrante": "Cuadrante A"
            },
            {
                "id": 2,
                "nombre": "Estación 002",
                "descripcion": "Estación de Prueba 2",
                "coordinador": "María García",
                "cuadrante": "Cuadrante B"
            }
        ]

        self.ordenes = {
            1: [
                {
                    "id": 1,
                    "ordenFabricacion": "OF-001",
                    "pt": "PT-001",
                    "cantidadFabricar": 1000,
                    "ptDescripcion": "Producto de Prueba A",
                    "ptUPC": "123456789012"
                },
                {
                    "id": 2,
                    "ordenFabricacion": "OF-002",
                    "pt": "PT-002",
                    "cantidadFabricar": 500,
                    "ptDescripcion": "Producto de Prueba B",
                    "ptUPC": "987654321098"
                }
            ],
            2: [
                {
                    "id": 3,
                    "ordenFabricacion": "OF-003",
                    "pt": "PT-003",
                    "cantidadFabricar": 750,
                    "ptDescripcion": "Producto de Prueba C",
                    "ptUPC": "112233445566"
                }
            ]
        }

        # Colores del tema industrial
        self.colores = {
            'fondo': '#2b2b2b',
            'panel': '#3c3c3c',
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

    def mostrar(self):
        """Mostrar la interfaz industrial"""
        try:
            self.root = tk.Tk()
            self.configurar_ventana()
            self.crear_interfaz()
            self.iniciar_simulacion()
            logger.info("✅ Interfaz industrial mostrada")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"❌ Error mostrando interfaz: {e}")

    def configurar_ventana(self):
        """Configurar ventana principal"""
        try:
            self.root.title("Monitor Industrial SISPRO - MODO PRUEBA MAC")
            self.root.configure(bg=self.colores['fondo'])

            # Tamaño para Mac
            self.root.geometry("1200x800")
            self.root.attributes('-topmost', False)

            # Centrar ventana
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
            y = (self.root.winfo_screenheight() // 2) - (800 // 2)
            self.root.geometry(f"1200x800+{x}+{y}")

            # Configurar teclas de salida
            self.root.bind('<Escape>', self.salir)
            self.root.bind('<Command-q>', self.salir)

        except Exception as e:
            logger.error(f"❌ Error configurando ventana: {e}")

    def crear_interfaz(self):
        """Crear interfaz principal"""
        try:
            # Frame principal
            main_frame = tk.Frame(self.root, bg=self.colores['fondo'])
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Título principal
            titulo = tk.Label(
                main_frame,
                text="🍓 MONITOR INDUSTRIAL SISPRO - MODO PRUEBA",
                font=self.fuente_titulo,
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            )
            titulo.pack(pady=20)

            # Panel de información
            info_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            info_frame.pack(fill=tk.X, pady=10)

            # Información de la estación
            estacion_frame = tk.Frame(info_frame, bg=self.colores['panel'])
            estacion_frame.pack(pady=10)

            tk.Label(
                estacion_frame,
                text="Estación:",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=0, padx=10, sticky=tk.W)

            tk.Label(
                estacion_frame,
                textvariable=self.estacion_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=1, padx=10, sticky=tk.W)

            tk.Label(
                estacion_frame,
                text="Estado:",
                font=self.fuente_grande,
                fg=self.colores['texto'],
                bg=self.colores['panel']
            ).grid(row=0, column=2, padx=10, sticky=tk.W)

            tk.Label(
                estacion_frame,
                textvariable=self.estado_var,
                font=self.fuente_grande,
                fg=self.colores['accento'],
                bg=self.colores['panel']
            ).grid(row=0, column=3, padx=10, sticky=tk.W)

            # Panel de producción
            prod_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            prod_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            # Información de la orden
            orden_frame = tk.Frame(prod_frame, bg=self.colores['panel'])
            orden_frame.pack(fill=tk.X, pady=20)

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
            contador_frame = tk.Frame(prod_frame, bg=self.colores['panel'])
            contador_frame.pack(expand=True)

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
            meta_frame = tk.Frame(prod_frame, bg=self.colores['panel'])
            meta_frame.pack(pady=20)

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
                prod_frame,
                length=600,
                mode='determinate'
            )
            self.progreso_barra.pack(pady=20)

            # Botones de control
            botones_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
            botones_frame.pack(fill=tk.X, pady=10)

            btn_frame = tk.Frame(botones_frame, bg=self.colores['panel'])
            btn_frame.pack(pady=20)

            # Botón seleccionar estación
            btn_estacion = tk.Button(
                btn_frame,
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
                btn_frame,
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
                btn_frame,
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
                btn_frame,
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

            # Botón salir
            btn_salir = tk.Button(
                btn_frame,
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
            btn_salir.grid(row=1, column=1, padx=10, pady=5)

        except Exception as e:
            logger.error(f"❌ Error creando interfaz: {e}")

    def iniciar_simulacion(self):
        """Iniciar simulación de producción"""
        def simular_produccion():
            while self.running:
                try:
                    if self.estado_var.get() == "PRODUCIENDO" and self.upc_validado:
                        # Simular incremento de conteo
                        if random.random() < 0.3:  # 30% de probabilidad cada segundo
                            self.lecturas_acumuladas += random.randint(1, 3)
                            self.contador_var.set(str(self.lecturas_acumuladas))

                            # Actualizar progreso
                            if self.orden_actual:
                                meta = self.orden_actual['cantidadFabricar']
                                if meta > 0:
                                    progreso = (self.lecturas_acumuladas / meta) * 100
                                    self.progreso_var.set(f"{progreso:.1f}%")
                                    self.progreso_barra['value'] = progreso

                            logger.info(f"📊 Conteo simulado: {self.lecturas_acumuladas}")

                    time.sleep(1)
                except Exception as e:
                    logger.error(f"❌ Error en simulación: {e}")
                    time.sleep(1)

        self.running = True
        thread = threading.Thread(target=simular_produccion, daemon=True)
        thread.start()

    def seleccionar_estacion(self):
        """Seleccionar estación de trabajo"""
        try:
            # Crear ventana de selección
            ventana = tk.Toplevel(self.root)
            ventana.title("Seleccionar Estación")
            ventana.configure(bg=self.colores['fondo'])
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

            lista = tk.Listbox(
                lista_frame,
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                selectbackground=self.colores['accento'],
                height=10
            )
            lista.pack(fill=tk.BOTH, expand=True)

            # Agregar estaciones
            for estacion in self.estaciones:
                texto = f"{estacion['nombre']} - {estacion.get('descripcion', '')}"
                lista.insert(tk.END, texto)

            # Variable para resultado
            resultado = [None]

            def seleccionar():
                seleccion = lista.curselection()
                if seleccion:
                    resultado[0] = self.estaciones[seleccion[0]]
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

            # Esperar selección
            ventana.wait_window()

            if resultado[0]:
                self.estacion_actual = resultado[0]
                self.estacion_var.set(self.estacion_actual['nombre'])
                logger.info(f"✅ Estación seleccionada: {self.estacion_actual['nombre']}")
                messagebox.showinfo("Éxito", f"Estación seleccionada: {self.estacion_actual['nombre']}")

        except Exception as e:
            logger.error(f"❌ Error seleccionando estación: {e}")
            messagebox.showerror("Error", f"Error seleccionando estación: {e}")

    def seleccionar_orden(self):
        """Seleccionar orden de fabricación"""
        try:
            if not self.estacion_actual:
                messagebox.showwarning("Advertencia", "Primero seleccione una estación")
                return

            ordenes = self.ordenes.get(self.estacion_actual['id'], [])
            if not ordenes:
                messagebox.showwarning("Advertencia", "No hay órdenes asignadas a esta estación")
                return

            # Crear ventana de selección
            ventana = tk.Toplevel(self.root)
            ventana.title("Seleccionar Orden")
            ventana.configure(bg=self.colores['fondo'])
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

            lista = tk.Listbox(
                lista_frame,
                font=self.fuente_normal,
                fg=self.colores['texto'],
                bg=self.colores['panel'],
                selectbackground=self.colores['accento'],
                height=12
            )
            lista.pack(fill=tk.BOTH, expand=True)

            # Agregar órdenes
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

            # Esperar selección
            ventana.wait_window()

            if resultado[0]:
                self.orden_actual = resultado[0]
                self.orden_var.set(self.orden_actual['ordenFabricacion'])
                self.upc_var.set(self.orden_actual['ptUPC'])
                self.meta_var.set(str(self.orden_actual['cantidadFabricar']))
                self.estado_var.set("ESPERANDO_UPC")
                logger.info(f"✅ Orden seleccionada: {self.orden_actual['ordenFabricacion']}")
                messagebox.showinfo("Éxito", f"Orden seleccionada: {self.orden_actual['ordenFabricacion']}")

        except Exception as e:
            logger.error(f"❌ Error seleccionando orden: {e}")
            messagebox.showerror("Error", f"Error seleccionando orden: {e}")

    def validar_upc(self):
        """Validar código UPC"""
        try:
            if not self.orden_actual:
                messagebox.showwarning("Advertencia", "Primero seleccione una orden")
                return

            upc = simpledialog.askstring(
                "Validar UPC",
                "Ingrese el código UPC:",
                parent=self.root
            )

            if upc:
                if upc == self.orden_actual['ptUPC']:
                    self.upc_validado = upc
                    self.estado_var.set("PRODUCIENDO")
                    self.lecturas_acumuladas = 0
                    self.contador_var.set("0")
                    logger.info(f"✅ UPC validado: {upc}")
                    messagebox.showinfo("Éxito", "UPC válido. Producción iniciada.")
                else:
                    logger.warning(f"⚠️ UPC inválido: {upc}")
                    messagebox.showerror("Error", "UPC inválido. Verifique el código.")

        except Exception as e:
            logger.error(f"❌ Error validando UPC: {e}")
            messagebox.showerror("Error", f"Error validando UPC: {e}")

    def finalizar_orden(self):
        """Finalizar orden actual"""
        try:
            if not self.orden_actual:
                messagebox.showwarning("Advertencia", "No hay orden activa")
                return

            if messagebox.askyesno("Confirmar", "¿Finalizar la orden actual?"):
                self.orden_actual = None
                self.upc_validado = None
                self.lecturas_acumuladas = 0
                self.estado_var.set("INACTIVO")
                self.orden_var.set("N/A")
                self.upc_var.set("N/A")
                self.meta_var.set("0")
                self.contador_var.set("0")
                self.progreso_var.set("0%")
                self.progreso_barra['value'] = 0
                logger.info("✅ Orden finalizada")
                messagebox.showinfo("Éxito", "Orden finalizada correctamente.")

        except Exception as e:
            logger.error(f"❌ Error finalizando orden: {e}")
            messagebox.showerror("Error", f"Error finalizando orden: {e}")

    def salir(self, event=None):
        """Salir de la aplicación"""
        try:
            if messagebox.askyesno("Confirmar", "¿Salir del Monitor Industrial?"):
                self.running = False
                self.root.quit()
        except Exception as e:
            logger.error(f"❌ Error saliendo: {e}")
            self.root.quit()

def main():
    """Función principal"""
    try:
        print("🍓 Monitor Industrial SISPRO - MODO PRUEBA MAC")
        print("=" * 50)
        print("Esta es una versión de prueba que simula:")
        print("- Comunicación RS485 con Pico")
        print("- APIs de SISPRO")
        print("- Lecturas de producción")
        print("=" * 50)
        print()

        monitor = MonitorIndustrialMac()
        monitor.mostrar()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
