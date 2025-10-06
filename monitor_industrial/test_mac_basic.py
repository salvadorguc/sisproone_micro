#!/usr/bin/env python3
"""
Monitor Industrial SISPRO - Versión Básica para Mac
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

class MonitorIndustrialMac:
    def __init__(self):
        # Estado del sistema
        self.estacion_actual = None
        self.orden_actual = None
        self.upc_validado = None
        self.lecturas_acumuladas = 0
        self.running = False

        # Datos de prueba
        self.estaciones = [
            {"id": 1, "nombre": "Estación 001", "descripcion": "Estación de Prueba", "coordinador": "Juan Pérez"},
            {"id": 2, "nombre": "Estación 002", "descripcion": "Estación de Prueba 2", "coordinador": "María García"}
        ]

        self.ordenes = {
            1: [
                {"id": 1, "ordenFabricacion": "OF-001", "cantidadFabricar": 1000, "ptDescripcion": "Producto A", "ptUPC": "123456789012"},
                {"id": 2, "ordenFabricacion": "OF-002", "cantidadFabricar": 500, "ptDescripcion": "Producto B", "ptUPC": "987654321098"}
            ],
            2: [
                {"id": 3, "ordenFabricacion": "OF-003", "cantidadFabricar": 750, "ptDescripcion": "Producto C", "ptUPC": "112233445566"}
            ]
        }

        # Colores
        self.colores = {
            'fondo': '#2b2b2b',
            'panel': '#3c3c3c',
            'texto': '#ffffff',
            'accento': '#00ff00',
            'error': '#ff0000',
            'borde': '#444444'
        }

    def crear_interfaz(self):
        """Crear la interfaz principal"""
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Monitor Industrial SISPRO - MODO PRUEBA MAC")
        self.root.configure(bg=self.colores['fondo'])
        self.root.geometry("1200x800")

        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")

        # Variables de la interfaz
        self.contador_var = tk.StringVar(value="0")
        self.meta_var = tk.StringVar(value="0")
        self.progreso_var = tk.StringVar(value="0%")
        self.estado_var = tk.StringVar(value="INACTIVO")
        self.orden_var = tk.StringVar(value="N/A")
        self.upc_var = tk.StringVar(value="N/A")
        self.estacion_var = tk.StringVar(value="N/A")

        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.colores['fondo'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        titulo = tk.Label(
            main_frame,
            text="🍓 MONITOR INDUSTRIAL SISPRO - MODO PRUEBA",
            font=('Arial', 24, 'bold'),
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

        tk.Label(estacion_frame, text="Estación:", font=('Arial', 18, 'bold'), fg=self.colores['texto'], bg=self.colores['panel']).grid(row=0, column=0, padx=10, sticky=tk.W)
        tk.Label(estacion_frame, textvariable=self.estacion_var, font=('Arial', 18, 'bold'), fg=self.colores['accento'], bg=self.colores['panel']).grid(row=0, column=1, padx=10, sticky=tk.W)

        tk.Label(estacion_frame, text="Estado:", font=('Arial', 18, 'bold'), fg=self.colores['texto'], bg=self.colores['panel']).grid(row=0, column=2, padx=10, sticky=tk.W)
        tk.Label(estacion_frame, textvariable=self.estado_var, font=('Arial', 18, 'bold'), fg=self.colores['accento'], bg=self.colores['panel']).grid(row=0, column=3, padx=10, sticky=tk.W)

        # Panel de producción
        prod_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        prod_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Información de la orden
        orden_frame = tk.Frame(prod_frame, bg=self.colores['panel'])
        orden_frame.pack(fill=tk.X, pady=20)

        tk.Label(orden_frame, text="Orden:", font=('Arial', 18, 'bold'), fg=self.colores['texto'], bg=self.colores['panel']).grid(row=0, column=0, padx=20, sticky=tk.W)
        tk.Label(orden_frame, textvariable=self.orden_var, font=('Arial', 18, 'bold'), fg=self.colores['accento'], bg=self.colores['panel']).grid(row=0, column=1, padx=20, sticky=tk.W)

        tk.Label(orden_frame, text="UPC:", font=('Arial', 18, 'bold'), fg=self.colores['texto'], bg=self.colores['panel']).grid(row=0, column=2, padx=20, sticky=tk.W)
        tk.Label(orden_frame, textvariable=self.upc_var, font=('Arial', 18, 'bold'), fg=self.colores['accento'], bg=self.colores['panel']).grid(row=0, column=3, padx=20, sticky=tk.W)

        # Contador principal
        contador_frame = tk.Frame(prod_frame, bg=self.colores['panel'])
        contador_frame.pack(expand=True)

        tk.Label(contador_frame, text="CONTADOR", font=('Arial', 18, 'bold'), fg=self.colores['texto'], bg=self.colores['panel']).pack()

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

        tk.Label(meta_frame, text="META:", font=('Arial', 18, 'bold'), fg=self.colores['texto'], bg=self.colores['panel']).grid(row=0, column=0, padx=20, sticky=tk.W)
        tk.Label(meta_frame, textvariable=self.meta_var, font=('Arial', 18, 'bold'), fg=self.colores['accento'], bg=self.colores['panel']).grid(row=0, column=1, padx=20, sticky=tk.W)

        tk.Label(meta_frame, text="PROGRESO:", font=('Arial', 18, 'bold'), fg=self.colores['texto'], bg=self.colores['panel']).grid(row=0, column=2, padx=20, sticky=tk.W)
        tk.Label(meta_frame, textvariable=self.progreso_var, font=('Arial', 18, 'bold'), fg=self.colores['accento'], bg=self.colores['panel']).grid(row=0, column=3, padx=20, sticky=tk.W)

        # Barra de progreso
        self.progreso_barra = ttk.Progressbar(prod_frame, length=600, mode='determinate')
        self.progreso_barra.pack(pady=20)

        # Botones de control
        botones_frame = tk.Frame(main_frame, bg=self.colores['panel'], relief=tk.RAISED, bd=2)
        botones_frame.pack(fill=tk.X, pady=10)

        btn_frame = tk.Frame(botones_frame, bg=self.colores['panel'])
        btn_frame.pack(pady=20)

        # Botones
        btn_estacion = tk.Button(
            btn_frame,
            text="🏭 SELECCIONAR ESTACIÓN",
            font=('Arial', 18, 'bold'),
            fg=self.colores['texto'],
            bg=self.colores['borde'],
            relief=tk.RAISED,
            bd=3,
            command=self.seleccionar_estacion,
            width=20,
            height=2
        )
        btn_estacion.grid(row=0, column=0, padx=10, pady=5)

        btn_orden = tk.Button(
            btn_frame,
            text="📦 SELECCIONAR ORDEN",
            font=('Arial', 18, 'bold'),
            fg=self.colores['texto'],
            bg=self.colores['borde'],
            relief=tk.RAISED,
            bd=3,
            command=self.seleccionar_orden,
            width=20,
            height=2
        )
        btn_orden.grid(row=0, column=1, padx=10, pady=5)

        btn_upc = tk.Button(
            btn_frame,
            text="📱 VALIDAR UPC",
            font=('Arial', 18, 'bold'),
            fg=self.colores['texto'],
            bg=self.colores['borde'],
            relief=tk.RAISED,
            bd=3,
            command=self.validar_upc,
            width=20,
            height=2
        )
        btn_upc.grid(row=0, column=2, padx=10, pady=5)

        btn_finalizar = tk.Button(
            btn_frame,
            text="✅ FINALIZAR ORDEN",
            font=('Arial', 18, 'bold'),
            fg=self.colores['texto'],
            bg=self.colores['error'],
            relief=tk.RAISED,
            bd=3,
            command=self.finalizar_orden,
            width=20,
            height=2
        )
        btn_finalizar.grid(row=1, column=0, padx=10, pady=5)

        btn_salir = tk.Button(
            btn_frame,
            text="🚪 SALIR",
            font=('Arial', 18, 'bold'),
            fg=self.colores['texto'],
            bg=self.colores['error'],
            relief=tk.RAISED,
            bd=3,
            command=self.salir,
            width=20,
            height=2
        )
        btn_salir.grid(row=1, column=1, padx=10, pady=5)

        # Configurar teclas de salida
        self.root.bind('<Escape>', self.salir)
        self.root.bind('<Command-q>', self.salir)

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
                font=('Arial', 24, 'bold'),
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=20)

            # Lista de estaciones
            lista_frame = tk.Frame(frame, bg=self.colores['fondo'])
            lista_frame.pack(fill=tk.BOTH, expand=True, pady=20)

            lista = tk.Listbox(
                lista_frame,
                font=('Arial', 12),
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
                font=('Arial', 18, 'bold'),
                fg=self.colores['texto'],
                bg=self.colores['accento'],
                command=seleccionar,
                width=15
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="CANCELAR",
                font=('Arial', 18, 'bold'),
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
                font=('Arial', 24, 'bold'),
                fg=self.colores['accento'],
                bg=self.colores['fondo']
            ).pack(pady=20)

            # Lista de órdenes
            lista_frame = tk.Frame(frame, bg=self.colores['fondo'])
            lista_frame.pack(fill=tk.BOTH, expand=True, pady=20)

            lista = tk.Listbox(
                lista_frame,
                font=('Arial', 12),
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
                font=('Arial', 18, 'bold'),
                fg=self.colores['texto'],
                bg=self.colores['accento'],
                command=seleccionar,
                width=15
            ).pack(side=tk.LEFT, padx=10)

            tk.Button(
                botones_frame,
                text="CANCELAR",
                font=('Arial', 18, 'bold'),
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
                    self.iniciar_simulacion()
                else:
                    logger.warning(f"⚠️ UPC inválido: {upc}")
                    messagebox.showerror("Error", "UPC inválido. Verifique el código.")

        except Exception as e:
            logger.error(f"❌ Error validando UPC: {e}")
            messagebox.showerror("Error", f"Error validando UPC: {e}")

    def iniciar_simulacion(self):
        """Iniciar simulación de producción"""
        def simular_produccion():
            while self.running and self.estado_var.get() == "PRODUCIENDO":
                try:
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

    def ejecutar(self):
        """Ejecutar el monitor"""
        try:
            print("🍓 Monitor Industrial SISPRO - MODO PRUEBA MAC")
            print("=" * 50)
            print("Esta es una versión de prueba que simula:")
            print("- Comunicación RS485 con Pico")
            print("- APIs de SISPRO")
            print("- Lecturas de producción")
            print("=" * 50)
            print()

            self.crear_interfaz()
            logger.info("✅ Interfaz industrial creada")
            self.root.mainloop()

        except Exception as e:
            logger.error(f"❌ Error en ejecución: {e}")
            print(f"❌ Error fatal: {e}")

def main():
    """Función principal"""
    monitor = MonitorIndustrialMac()
    monitor.ejecutar()

if __name__ == "__main__":
    main()
