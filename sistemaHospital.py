import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                              QTableWidget, QTableWidgetItem, QComboBox, 
                              QDateEdit, QTimeEdit, QMessageBox, QTabWidget,
                              QTextEdit, QDialog, QFormLayout, QDialogButtonBox,
                              QHeaderView)
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
import json

class Usuario:
    def __init__(self, username, password, rol, nombre_completo):
        self.username = username
        self.password = password
        self.rol = rol  # 'paciente', 'medico', 'administrador'
        self.nombre_completo = nombre_completo

class Paciente:
    def __init__(self, id_paciente, nombre, apellido, telefono, email, fecha_nacimiento):
        self.id = id_paciente
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email
        self.fecha_nacimiento = fecha_nacimiento
        self.historial_citas = []

class Medico:
    def __init__(self, id_medico, nombre, apellido, especialidad):
        self.id = id_medico
        self.nombre = nombre
        self.apellido = apellido
        self.especialidad = especialidad
        self.horarios_disponibles = []

class Cita:
    def __init__(self, id_cita, paciente_id, medico_id, fecha, hora, estado="Programada"):
        self.id = id_cita
        self.paciente_id = paciente_id
        self.medico_id = medico_id
        self.fecha = fecha
        self.hora = hora
        self.estado = estado  # Programada, Completada, Cancelada
        self.fecha_creacion = datetime.now()

class SistemaHospital:
    def __init__(self):
        self.usuarios = {}
        self.pacientes = {}
        self.medicos = {}
        self.citas = {}
        self.siguiente_id_paciente = 1
        self.siguiente_id_medico = 1
        self.siguiente_id_cita = 1
        self.auditoria = []
        self._inicializar_datos()

    def _inicializar_datos(self):
        # Usuarios por defecto
        self.usuarios['admin'] = Usuario('admin', 'admin123', 'administrador', 'Administrador Sistema')
        self.usuarios['medico1'] = Usuario('medico1', 'med123', 'medico', 'Dr. Juan Pérez')
        self.usuarios['paciente1'] = Usuario('paciente1', 'pac123', 'paciente', 'María García')
        
        # Médicos por defecto
        medico1 = Medico(1, 'Juan', 'Pérez', 'Cardiología')
        medico2 = Medico(2, 'Ana', 'Martínez', 'Pediatría')
        medico3 = Medico(3, 'Carlos', 'López', 'Medicina General')
        self.medicos[1] = medico1
        self.medicos[2] = medico2
        self.medicos[3] = medico3
        self.siguiente_id_medico = 4

    def autenticar(self, username, password):
        usuario = self.usuarios.get(username)
        if usuario and usuario.password == password:
            self.registrar_auditoria(f"Login exitoso: {username} ({usuario.rol})")
            return usuario
        self.registrar_auditoria(f"Intento de login fallido: {username}")
        return None

    def registrar_usuario(self, username, password, rol, nombre_completo):
        if username in self.usuarios:
            return False
        self.usuarios[username] = Usuario(username, password, rol, nombre_completo)
        self.registrar_auditoria(f"Nuevo usuario registrado: {username} ({rol})")
        return True

    def registrar_paciente(self, nombre, apellido, telefono, email, fecha_nacimiento):
        paciente = Paciente(self.siguiente_id_paciente, nombre, apellido, telefono, email, fecha_nacimiento)
        self.pacientes[self.siguiente_id_paciente] = paciente
        self.registrar_auditoria(f"Nuevo paciente registrado: {nombre} {apellido} (ID: {self.siguiente_id_paciente})")
        self.siguiente_id_paciente += 1
        return paciente

    def registrar_medico(self, nombre, apellido, especialidad):
        medico = Medico(self.siguiente_id_medico, nombre, apellido, especialidad)
        self.medicos[self.siguiente_id_medico] = medico
        self.registrar_auditoria(f"Nuevo médico registrado: {nombre} {apellido} (ID: {self.siguiente_id_medico})")
        self.siguiente_id_medico += 1
        return medico

    def crear_cita(self, paciente_id, medico_id, fecha, hora):
        if not self._horario_disponible(medico_id, fecha, hora):
            return None
        cita = Cita(self.siguiente_id_cita, paciente_id, medico_id, fecha, hora)
        self.citas[self.siguiente_id_cita] = cita
        
        paciente = self.pacientes[paciente_id]
        medico = self.medicos[medico_id]
        paciente.historial_citas.append(self.siguiente_id_cita)
        
        self.registrar_auditoria(f"Cita creada: ID {self.siguiente_id_cita} - Paciente {paciente.nombre} {paciente.apellido} con Dr. {medico.nombre} {medico.apellido}")
        self.siguiente_id_cita += 1
        return cita

    def _horario_disponible(self, medico_id, fecha, hora):
        for cita in self.citas.values():
            if (cita.medico_id == medico_id and 
                cita.fecha == fecha and 
                cita.hora == hora and 
                cita.estado == "Programada"):
                return False
        return True

    def cancelar_cita(self, cita_id):
        if cita_id in self.citas:
            cita = self.citas[cita_id]
            cita.estado = "Cancelada"
            self.registrar_auditoria(f"Cita cancelada: ID {cita_id}")
            return True
        return False

    def completar_cita(self, cita_id):
        if cita_id in self.citas:
            cita = self.citas[cita_id]
            cita.estado = "Completada"
            self.registrar_auditoria(f"Cita completada: ID {cita_id}")
            return True
        return False

    def registrar_auditoria(self, evento):
        registro = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'evento': evento
        }
        self.auditoria.append(registro)

class DialogoNuevoPaciente(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Nuevo Paciente")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.nombre_input = QLineEdit()
        self.apellido_input = QLineEdit()
        self.telefono_input = QLineEdit()
        self.email_input = QLineEdit()
        self.fecha_nac_input = QDateEdit()
        self.fecha_nac_input.setDate(QDate.currentDate().addYears(-30))
        self.fecha_nac_input.setCalendarPopup(True)
        
        layout.addRow("Nombre:", self.nombre_input)
        layout.addRow("Apellido:", self.apellido_input)
        layout.addRow("Teléfono:", self.telefono_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Fecha Nacimiento:", self.fecha_nac_input)
        
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        
        layout.addRow(botones)
        self.setLayout(layout)

class DialogoNuevaCita(QDialog):
    def __init__(self, sistema, parent=None):
        super().__init__(parent)
        self.sistema = sistema
        self.setWindowTitle("Agendar Nueva Cita")
        self.setMinimumWidth(400)
        
        layout = QFormLayout()
        
        self.paciente_combo = QComboBox()
        for id_pac, paciente in sistema.pacientes.items():
            self.paciente_combo.addItem(f"{paciente.nombre} {paciente.apellido} (ID: {id_pac})", id_pac)
        
        self.medico_combo = QComboBox()
        for id_med, medico in sistema.medicos.items():
            self.medico_combo.addItem(f"Dr. {medico.nombre} {medico.apellido} - {medico.especialidad}", id_med)
        
        self.fecha_input = QDateEdit()
        self.fecha_input.setDate(QDate.currentDate().addDays(1))
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setMinimumDate(QDate.currentDate())
        
        self.hora_input = QTimeEdit()
        self.hora_input.setTime(QTime(9, 0))
        
        layout.addRow("Paciente:", self.paciente_combo)
        layout.addRow("Médico:", self.medico_combo)
        layout.addRow("Fecha:", self.fecha_input)
        layout.addRow("Hora:", self.hora_input)
        
        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        
        layout.addRow(botones)
        self.setLayout(layout)

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sistema = SistemaHospital()
        self.usuario_actual = None
        self.iniciar_sesion()

    def iniciar_sesion(self):
        dialog = QDialog()
        dialog.setWindowTitle("Sistema de Gestión Hospitalaria - Login")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        titulo = QLabel("Iniciar Sesión")
        titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        form_layout = QFormLayout()
        username_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Usuario:", username_input)
        form_layout.addRow("Contraseña:", password_input)
        layout.addLayout(form_layout)
        
        btn_login = QPushButton("Iniciar Sesión")
        layout.addWidget(btn_login)
        
        info_label = QLabel("Usuarios de prueba:\nadmin/admin123\nmedico1/med123\npaciente1/pac123")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)
        
        def intentar_login():
            usuario = self.sistema.autenticar(username_input.text(), password_input.text())
            if usuario:
                self.usuario_actual = usuario
                dialog.accept()
                self.inicializar_ui()
            else:
                QMessageBox.warning(dialog, "Error", "Usuario o contraseña incorrectos")
        
        btn_login.clicked.connect(intentar_login)
        password_input.returnPressed.connect(intentar_login)
        
        dialog.setLayout(layout)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            sys.exit()

    def inicializar_ui(self):
        self.setWindowTitle(f"Sistema de Gestión Hospitalaria - {self.usuario_actual.nombre_completo} ({self.usuario_actual.rol})")
        self.setGeometry(100, 100, 1200, 700)
        
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout = QVBoxLayout(widget_central)
        
        # Header
        header = QLabel(f"Bienvenido: {self.usuario_actual.nombre_completo}")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        
        if self.usuario_actual.rol in ['administrador', 'medico']:
            self.tabs.addTab(self.crear_tab_pacientes(), "Pacientes")
        
        if self.usuario_actual.rol in ['administrador']:
            self.tabs.addTab(self.crear_tab_medicos(), "Médicos")
        
        self.tabs.addTab(self.crear_tab_citas(), "Citas")
        
        if self.usuario_actual.rol in ['administrador']:
            self.tabs.addTab(self.crear_tab_auditoria(), "Auditoría")
        
        layout.addWidget(self.tabs)
        
        # Botón cerrar sesión
        btn_logout = QPushButton("Cerrar Sesión")
        btn_logout.clicked.connect(self.cerrar_sesion)
        layout.addWidget(btn_logout)
        
        self.show()

    def crear_tab_pacientes(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_nuevo = QPushButton("Registrar Nuevo Paciente")
        btn_nuevo.clicked.connect(self.registrar_paciente)
        btn_actualizar = QPushButton("Actualizar Lista")
        btn_actualizar.clicked.connect(self.actualizar_tabla_pacientes)
        btn_layout.addWidget(btn_nuevo)
        btn_layout.addWidget(btn_actualizar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Tabla
        self.tabla_pacientes = QTableWidget()
        self.tabla_pacientes.setColumnCount(6)
        self.tabla_pacientes.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Teléfono", "Email", "Fecha Nacimiento"])
        self.tabla_pacientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_pacientes)
        
        self.actualizar_tabla_pacientes()
        return tab

    def crear_tab_medicos(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tabla
        self.tabla_medicos = QTableWidget()
        self.tabla_medicos.setColumnCount(4)
        self.tabla_medicos.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Especialidad"])
        self.tabla_medicos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_medicos)
        
        self.actualizar_tabla_medicos()
        return tab

    def crear_tab_citas(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_nueva = QPushButton("Agendar Nueva Cita")
        btn_nueva.clicked.connect(self.agendar_cita)
        btn_cancelar = QPushButton("Cancelar Cita Seleccionada")
        btn_cancelar.clicked.connect(self.cancelar_cita)
        btn_completar = QPushButton("Completar Cita Seleccionada")
        btn_completar.clicked.connect(self.completar_cita)
        btn_actualizar = QPushButton("Actualizar Lista")
        btn_actualizar.clicked.connect(self.actualizar_tabla_citas)
        
        btn_layout.addWidget(btn_nueva)
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_completar)
        btn_layout.addWidget(btn_actualizar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Tabla
        self.tabla_citas = QTableWidget()
        self.tabla_citas.setColumnCount(7)
        self.tabla_citas.setHorizontalHeaderLabels(["ID", "Paciente", "Médico", "Especialidad", "Fecha", "Hora", "Estado"])
        self.tabla_citas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_citas)
        
        self.actualizar_tabla_citas()
        return tab

    def crear_tab_auditoria(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        btn_actualizar = QPushButton("Actualizar Auditoría")
        btn_actualizar.clicked.connect(self.actualizar_auditoria)
        layout.addWidget(btn_actualizar)
        
        self.texto_auditoria = QTextEdit()
        self.texto_auditoria.setReadOnly(True)
        layout.addWidget(self.texto_auditoria)
        
        self.actualizar_auditoria()
        return tab

    def registrar_paciente(self):
        dialog = DialogoNuevoPaciente(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.sistema.registrar_paciente(
                dialog.nombre_input.text(),
                dialog.apellido_input.text(),
                dialog.telefono_input.text(),
                dialog.email_input.text(),
                dialog.fecha_nac_input.date().toString("yyyy-MM-dd")
            )
            self.actualizar_tabla_pacientes()
            QMessageBox.information(self, "Éxito", "Paciente registrado correctamente")

    def agendar_cita(self):
        if not self.sistema.pacientes:
            QMessageBox.warning(self, "Error", "Debe registrar al menos un paciente primero")
            return
        
        dialog = DialogoNuevaCita(self.sistema, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            cita = self.sistema.crear_cita(
                dialog.paciente_combo.currentData(),
                dialog.medico_combo.currentData(),
                dialog.fecha_input.date().toString("yyyy-MM-dd"),
                dialog.hora_input.time().toString("HH:mm")
            )
            if cita:
                self.actualizar_tabla_citas()
                QMessageBox.information(self, "Éxito", "Cita agendada correctamente")
            else:
                QMessageBox.warning(self, "Error", "El horario seleccionado no está disponible")

    def cancelar_cita(self):
        fila_actual = self.tabla_citas.currentRow()
        if fila_actual >= 0:
            cita_id = int(self.tabla_citas.item(fila_actual, 0).text())
            if self.sistema.cancelar_cita(cita_id):
                self.actualizar_tabla_citas()
                QMessageBox.information(self, "Éxito", "Cita cancelada correctamente")
        else:
            QMessageBox.warning(self, "Error", "Seleccione una cita")

    def completar_cita(self):
        fila_actual = self.tabla_citas.currentRow()
        if fila_actual >= 0:
            cita_id = int(self.tabla_citas.item(fila_actual, 0).text())
            if self.sistema.completar_cita(cita_id):
                self.actualizar_tabla_citas()
                QMessageBox.information(self, "Éxito", "Cita completada correctamente")
        else:
            QMessageBox.warning(self, "Error", "Seleccione una cita")

    def actualizar_tabla_pacientes(self):
        self.tabla_pacientes.setRowCount(0)
        for paciente in self.sistema.pacientes.values():
            fila = self.tabla_pacientes.rowCount()
            self.tabla_pacientes.insertRow(fila)
            self.tabla_pacientes.setItem(fila, 0, QTableWidgetItem(str(paciente.id)))
            self.tabla_pacientes.setItem(fila, 1, QTableWidgetItem(paciente.nombre))
            self.tabla_pacientes.setItem(fila, 2, QTableWidgetItem(paciente.apellido))
            self.tabla_pacientes.setItem(fila, 3, QTableWidgetItem(paciente.telefono))
            self.tabla_pacientes.setItem(fila, 4, QTableWidgetItem(paciente.email))
            self.tabla_pacientes.setItem(fila, 5, QTableWidgetItem(paciente.fecha_nacimiento))

    def actualizar_tabla_medicos(self):
        self.tabla_medicos.setRowCount(0)
        for medico in self.sistema.medicos.values():
            fila = self.tabla_medicos.rowCount()
            self.tabla_medicos.insertRow(fila)
            self.tabla_medicos.setItem(fila, 0, QTableWidgetItem(str(medico.id)))
            self.tabla_medicos.setItem(fila, 1, QTableWidgetItem(medico.nombre))
            self.tabla_medicos.setItem(fila, 2, QTableWidgetItem(medico.apellido))
            self.tabla_medicos.setItem(fila, 3, QTableWidgetItem(medico.especialidad))

    def actualizar_tabla_citas(self):
        self.tabla_citas.setRowCount(0)
        for cita in self.sistema.citas.values():
            paciente = self.sistema.pacientes.get(cita.paciente_id)
            medico = self.sistema.medicos.get(cita.medico_id)
            
            fila = self.tabla_citas.rowCount()
            self.tabla_citas.insertRow(fila)
            self.tabla_citas.setItem(fila, 0, QTableWidgetItem(str(cita.id)))
            self.tabla_citas.setItem(fila, 1, QTableWidgetItem(f"{paciente.nombre} {paciente.apellido}"))
            self.tabla_citas.setItem(fila, 2, QTableWidgetItem(f"Dr. {medico.nombre} {medico.apellido}"))
            self.tabla_citas.setItem(fila, 3, QTableWidgetItem(medico.especialidad))
            self.tabla_citas.setItem(fila, 4, QTableWidgetItem(cita.fecha))
            self.tabla_citas.setItem(fila, 5, QTableWidgetItem(cita.hora))
            self.tabla_citas.setItem(fila, 6, QTableWidgetItem(cita.estado))

    def actualizar_auditoria(self):
        texto = ""
        for registro in reversed(self.sistema.auditoria[-50:]):  # Últimos 50 registros
            texto += f"[{registro['timestamp']}] {registro['evento']}\n"
        self.texto_auditoria.setText(texto)

    def cerrar_sesion(self):
        self.close()
        self.usuario_actual = None
        self.iniciar_sesion()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    sys.exit(app.exec())