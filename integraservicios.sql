-- Tabla Usuario
CREATE TABLE Usuario (
    ID_Usuario SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Telefono VARCHAR(15),
    Contrasena VARCHAR(255) NOT NULL
);

-- Tabla Tipo_Recurso
CREATE TABLE Tipo_Recurso (
    ID_Tipo_Recurso SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL
);

-- Tabla Recurso
CREATE TABLE Recurso (
    ID_Recurso SERIAL PRIMARY KEY,
    ID_Tipo_Recurso INT NOT NULL,
    Nombre VARCHAR(100) NOT NULL,
    Horario_Disponibilidad VARCHAR(255),
    Estado VARCHAR(50) DEFAULT 'Disponible',
    FOREIGN KEY (ID_Tipo_Recurso) REFERENCES Tipo_Recurso(ID_Tipo_Recurso)
);

-- Tabla Reserva
CREATE TABLE Reserva (
    ID_Reserva SERIAL PRIMARY KEY,
    ID_Usuario INT NOT NULL,
    ID_Recurso INT NOT NULL,
    Fecha_Reserva DATE NOT NULL,
    Hora_Reserva TIME NOT NULL,
    Estado VARCHAR(50) DEFAULT 'Vigente',
    FOREIGN KEY (ID_Usuario) REFERENCES Usuario(ID_Usuario),
    FOREIGN KEY (ID_Recurso) REFERENCES Recurso(ID_Recurso)
);

-- Tabla Prestamo
CREATE TABLE Prestamo (
    ID_Prestamo SERIAL PRIMARY KEY,
    ID_Reserva INT NOT NULL,
    ID_Empleado INT NOT NULL,
    Fecha_Prestamo DATE NOT NULL,
    Hora_Prestamo TIME NOT NULL,
    FOREIGN KEY (ID_Reserva) REFERENCES Reserva(ID_Reserva)
);

-- Tabla Devolucion
CREATE TABLE Devolucion (
    ID_Devolucion SERIAL PRIMARY KEY,
    ID_Prestamo INT NOT NULL,
    Fecha_Devolucion DATE NOT NULL,
    Hora_Devolucion TIME NOT NULL,
    FOREIGN KEY (ID_Prestamo) REFERENCES Prestamo(ID_Prestamo)
);

-- Tabla Empleado
CREATE TABLE Empleado (
    ID_Empleado SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Cargo VARCHAR(50) NOT NULL
);

-- Datos de prueba

-- Usuarios
INSERT INTO Usuario (Nombre, Email, Telefono, Contrasena) VALUES
('Juan Pérez', 'juan.perez@example.com', '1234567890', 'password123'),
('María López', 'maria.lopez@example.com', '0987654321', 'securepass'),
('Pedro Alvarado', 'pedro.alvarado@example.com', '9876543210', 'pass456'),
('Sofía Ramírez', 'sofia.ramirez@example.com', '5678901234', 'mypassword');

-- Tipos de Recurso
INSERT INTO Tipo_Recurso (Nombre) VALUES
('Salón'),
('Laboratorio'),
('Cancha Deportiva'),
('Auditorio');

-- Recursos
INSERT INTO Recurso (ID_Tipo_Recurso, Nombre, Horario_Disponibilidad, Estado) VALUES
(1, 'Salón 101', 'Lunes a Viernes 07:00-19:00', 'Disponible'),
(1, 'Salón 102', 'Lunes a Viernes 08:00-18:00', 'Disponible'),
(2, 'Laboratorio Químico', 'Lunes a Viernes 08:00-18:00', 'Disponible'),
(3, 'Cancha de Fútbol', 'Lunes a Domingo 07:00-21:00', 'Disponible'),
(4, 'Auditorio Principal', 'Lunes a Viernes 09:00-20:00', 'Disponible');

-- Reservas
INSERT INTO Reserva (ID_Usuario, ID_Recurso, Fecha_Reserva, Hora_Reserva, Estado) VALUES
(1, 1, '2025-01-23', '09:00:00', 'Vigente'),
(2, 3, '2025-01-24', '15:00:00', 'Futura'),
(3, 4, '2025-01-25', '10:00:00', 'Vigente'),
(4, 2, '2025-01-26', '11:00:00', 'Futura');

-- Empleados
INSERT INTO Empleado (Nombre, Cargo) VALUES
('Carlos Gómez', 'Recepcionista'),
('Ana Martínez', 'Encargada de Recursos'),
('Luis Fernández', 'Supervisor');

-- Préstamos
INSERT INTO Prestamo (ID_Reserva, ID_Empleado, Fecha_Prestamo, Hora_Prestamo) VALUES
(1, 1, '2025-01-23', '08:55:00'),
(3, 2, '2025-01-25', '09:55:00');

-- Devoluciones
INSERT INTO Devolucion (ID_Prestamo, Fecha_Devolucion, Hora_Devolucion) VALUES
(1, '2025-01-23', '10:00:00'),
(2, '2025-01-25', '12:00:00');
