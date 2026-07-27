import DataFrameToBigQuery
import RolimonsETL
import RolimonsDataExtraction
import RandomForestBigQuery
import sys
import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal, Slot, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTextEdit
)

def historyAdd():
  APIdata = RolimonsDataExtraction.ExtractFromAPI()
  dataframe = RolimonsETL.CreateDataFrame(APIdata)
  DataFrameToBigQuery.sync_to_bigquery(dataframe)

# --- TRABAJADOR PROCESO 1 (Diario) ---
class DiarioWorker(QObject):
    log_signal = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.is_running = True

    @Slot()
    def run(self):
        # Primera ejecución inmediata
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P1: Primera ejecución iniciada (Inmediata).")
        self.ejecutar_tarea()

        # Bucle para ejecuciones posteriores (Cada 24 horas)
        # NOTA: Para probarlo rápido sin esperar 24h, cambia 86400 por un número menor (ej. 10)
        SEGUNDOS_DIARIOS = 86400 
        
        while self.is_running:
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P1: Programado para la próxima ejecución diaria.")
            
            # Dormimos en pequeños intervalos para permitir detener el hilo limpiamente
            for _ in range(SEGUNDOS_DIARIOS):
                if not self.is_running:
                    break
                time.sleep(1)

            if self.is_running:
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P1: Ejecutando tarea diaria habitual...")
                self.ejecutar_tarea()

    def ejecutar_tarea(self):
        try:
            historyAdd()
            RandomForestBigQuery.generate_daily_predictions()
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P1: Tarea diaria completada con éxito.")
        except Exception as e:
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P1: Ha habido errores: {e}.")

    def stop(self):
        self.is_running = False


# --- TRABAJADOR PROCESO 2 (Semanal) ---
class SemanalWorker(QObject):
    log_signal = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.is_running = True

    @Slot()
    def run(self):
        # Primera ejecución inmediata
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P2: Primera ejecución iniciada (Inmediata).")
        self.ejecutar_tarea()

        # Bucle para ejecuciones posteriores (Cada 7 días)
        SEGUNDOS_SEMANALES = 604800
        
        while self.is_running:
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P2: Programado para la próxima ejecución semanal.")
            
            for _ in range(SEGUNDOS_SEMANALES):
                if not self.is_running:
                    break
                time.sleep(1)

            if self.is_running:
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P2: Ejecutando tarea semanal habitual...")
                self.ejecutar_tarea()

    def ejecutar_tarea(self):
        # Simulación de procesamiento
        time.sleep(3)
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] P2: Tarea semanal completada con éxito.")

    def stop(self):
        self.is_running = False


# --- INTERFAZ GRÁFICA ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de Procesos Hilados")
        self.resize(600, 400)

        # Variables para los hilos y workers
        self.thread_p1 = None
        self.worker_p1 = None
        self.thread_p2 = None
        self.worker_p2 = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Botones
        button_layout = QHBoxLayout()
        self.btn_p1 = QPushButton("Iniciar Historico y Predicción (Diario)")
        self.btn_p2 = QPushButton("Iniciar Entrenamiento (Semanal)")
        
        button_layout.addWidget(self.btn_p1)
        button_layout.addWidget(self.btn_p2)

        # Consola gráfica
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas, Monospace;")

        layout.addLayout(button_layout)
        layout.addWidget(self.console)

        # Conectar botones
        self.btn_p1.clicked.connect(self.toggle_proceso_1)
        self.btn_p2.clicked.connect(self.toggle_proceso_2)

    @Slot(str)
    def append_log(self, text):
        """Añade texto a la consola visual."""
        self.console.append(text)

    def toggle_proceso_1(self):
        if self.thread_p1 is None or not self.thread_p1.isRunning():
            # Crear hilo y worker
            self.thread_p1 = QThread()
            self.worker_p1 = DiarioWorker()
            self.worker_p1.moveToThread(self.thread_p1)

            # Conexiones
            self.thread_p1.started.connect(self.worker_p1.run)
            self.worker_p1.log_signal.connect(self.append_log)

            self.thread_p1.start()
            self.btn_p1.setText("Detener Historico y Predicción")
            self.append_log("--- Historico y Predicción Iniciado ---")
        else:
            # Detener ordenadamente
            self.worker_p1.stop()
            self.thread_p1.quit()
            self.thread_p1.wait()
            self.btn_p1.setText("Iniciar Historico y Predicción (Diario)")
            self.append_log("--- Historico y Predicción Detenido ---")

    def toggle_proceso_2(self):
        if self.thread_p2 is None or not self.thread_p2.isRunning():
            # Crear hilo y worker
            self.thread_p2 = QThread()
            self.worker_p2 = SemanalWorker()
            self.worker_p2.moveToThread(self.thread_p2)

            # Conexiones
            self.thread_p2.started.connect(self.worker_p2.run)
            self.worker_p2.log_signal.connect(self.append_log)

            self.thread_p2.start()
            self.btn_p2.setText("Detener Entrenamiento")
            self.append_log("--- Entrenamiento Semanal Iniciado ---")
        else:
            # Detener ordenadamente
            self.worker_p2.stop()
            self.thread_p2.quit()
            self.thread_p2.wait()
            self.btn_p2.setText("Iniciar Entrenamiento (Semanal)")
            self.append_log("--- Entrenamiento Detenido ---")

    def closeEvent(self, event):
        # Asegura que los hilos se cierren al cerrar la ventana.
        if self.worker_p1: self.worker_p1.stop()
        if self.worker_p2: self.worker_p2.stop()
        if self.thread_p1: self.thread_p1.quit(); self.thread_p1.wait()
        if self.thread_p2: self.thread_p2.quit(); self.thread_p2.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.argv and sys.exit(app.exec())