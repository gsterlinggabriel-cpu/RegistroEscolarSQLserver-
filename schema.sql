IF DB_ID(N'RegistroEscolar') IS NULL
    CREATE DATABASE RegistroEscolar;
GO

USE RegistroEscolar;
GO

IF OBJECT_ID(N'dbo.estudiantes', N'U') IS NULL
CREATE TABLE dbo.estudiantes (
    id INT IDENTITY(1,1) NOT NULL,
    nombres NVARCHAR(100) NOT NULL,
    apellidos NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_estudiantes PRIMARY KEY (id)
);
GO

IF OBJECT_ID(N'dbo.docentes', N'U') IS NULL
CREATE TABLE dbo.docentes (
    id INT IDENTITY(1,1) NOT NULL,
    nombres NVARCHAR(100) NOT NULL,
    apellidos NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_docentes PRIMARY KEY (id)
);
GO

IF OBJECT_ID(N'dbo.periodos', N'U') IS NULL
CREATE TABLE dbo.periodos (
    id INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(50) NOT NULL,
    CONSTRAINT PK_periodos PRIMARY KEY (id),
    CONSTRAINT UQ_periodos_nombre UNIQUE (nombre)
);
GO

IF OBJECT_ID(N'dbo.usuarios', N'U') IS NULL
CREATE TABLE dbo.usuarios (
    id INT IDENTITY(1,1) NOT NULL,
    nombre_usuario NVARCHAR(50) NOT NULL,
    contrasena NVARCHAR(255) NOT NULL,
    rol NVARCHAR(20) NOT NULL,
    CONSTRAINT PK_usuarios PRIMARY KEY (id),
    CONSTRAINT UQ_usuarios_usuario UNIQUE (nombre_usuario),
    CONSTRAINT CK_usuarios_rol CHECK (rol IN (N'admin', N'docente', N'secretaria'))
);
GO

IF OBJECT_ID(N'dbo.materias', N'U') IS NULL
CREATE TABLE dbo.materias (
    id INT IDENTITY(1,1) NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    docente_id INT NULL,
    CONSTRAINT PK_materias PRIMARY KEY (id),
    CONSTRAINT UQ_materias_nombre UNIQUE (nombre),
    CONSTRAINT FK_materias_docentes FOREIGN KEY (docente_id)
        REFERENCES dbo.docentes (id)
        ON DELETE SET NULL
);
GO

IF OBJECT_ID(N'dbo.matriculas', N'U') IS NULL
CREATE TABLE dbo.matriculas (
    id INT IDENTITY(1,1) NOT NULL,
    estudiante_id INT NOT NULL,
    ano_escolar NVARCHAR(9) NOT NULL,
    CONSTRAINT PK_matriculas PRIMARY KEY (id),
    CONSTRAINT UQ_matriculas_estudiante_ano UNIQUE (estudiante_id, ano_escolar),
    CONSTRAINT FK_matriculas_estudiantes FOREIGN KEY (estudiante_id)
        REFERENCES dbo.estudiantes (id)
);
GO

IF OBJECT_ID(N'dbo.asistencia', N'U') IS NULL
CREATE TABLE dbo.asistencia (
    id INT IDENTITY(1,1) NOT NULL,
    matricula_id INT NOT NULL,
    fecha DATE NOT NULL,
    estado NVARCHAR(15) NOT NULL,
    CONSTRAINT PK_asistencia PRIMARY KEY (id),
    CONSTRAINT UQ_asistencia_matricula_fecha UNIQUE (matricula_id, fecha),
    CONSTRAINT CK_asistencia_estado CHECK (estado IN (N'Presente', N'Ausente', N'Tardanza', N'Excusa')),
    CONSTRAINT FK_asistencia_matriculas FOREIGN KEY (matricula_id)
        REFERENCES dbo.matriculas (id)
        ON DELETE CASCADE
);
GO

IF OBJECT_ID(N'dbo.calificaciones', N'U') IS NULL
CREATE TABLE dbo.calificaciones (
    id INT IDENTITY(1,1) NOT NULL,
    matricula_id INT NOT NULL,
    materia_id INT NOT NULL,
    periodo_id INT NOT NULL,
    nota DECIMAL(5,2) NOT NULL,
    CONSTRAINT PK_calificaciones PRIMARY KEY (id),
    CONSTRAINT UQ_calificaciones_matricula_materia_periodo UNIQUE (matricula_id, materia_id, periodo_id),
    CONSTRAINT CK_calificaciones_nota CHECK (nota BETWEEN 0 AND 100),
    CONSTRAINT FK_calificaciones_matriculas FOREIGN KEY (matricula_id)
        REFERENCES dbo.matriculas (id)
        ON DELETE CASCADE,
    CONSTRAINT FK_calificaciones_materias FOREIGN KEY (materia_id)
        REFERENCES dbo.materias (id),
    CONSTRAINT FK_calificaciones_periodos FOREIGN KEY (periodo_id)
        REFERENCES dbo.periodos (id)
);
GO

IF OBJECT_ID(N'dbo.calificaciones_finales', N'U') IS NULL
CREATE TABLE dbo.calificaciones_finales (
    id INT IDENTITY(1,1) NOT NULL,
    matricula_id INT NOT NULL,
    materia_id INT NOT NULL,
    nota_final DECIMAL(5,2) NOT NULL,
    CONSTRAINT PK_calificaciones_finales PRIMARY KEY (id),
    CONSTRAINT UQ_calificaciones_finales_matricula_materia UNIQUE (matricula_id, materia_id),
    CONSTRAINT CK_calificaciones_finales_nota CHECK (nota_final BETWEEN 0 AND 100),
    CONSTRAINT FK_calificaciones_finales_matriculas FOREIGN KEY (matricula_id)
        REFERENCES dbo.matriculas (id)
        ON DELETE CASCADE,
    CONSTRAINT FK_calificaciones_finales_materias FOREIGN KEY (materia_id)
        REFERENCES dbo.materias (id)
);
GO

IF OBJECT_ID(N'dbo.alertas', N'U') IS NULL
CREATE TABLE dbo.alertas (
    id INT IDENTITY(1,1) NOT NULL,
    matricula_id INT NOT NULL,
    mensaje NVARCHAR(500) NOT NULL,
    CONSTRAINT PK_alertas PRIMARY KEY (id),
    CONSTRAINT FK_alertas_matriculas FOREIGN KEY (matricula_id)
        REFERENCES dbo.matriculas (id)
        ON DELETE CASCADE
);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_materias_docente' AND object_id = OBJECT_ID(N'dbo.materias'))
    CREATE INDEX IX_materias_docente ON dbo.materias (docente_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_calificaciones_materia' AND object_id = OBJECT_ID(N'dbo.calificaciones'))
    CREATE INDEX IX_calificaciones_materia ON dbo.calificaciones (materia_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_calificaciones_periodo' AND object_id = OBJECT_ID(N'dbo.calificaciones'))
    CREATE INDEX IX_calificaciones_periodo ON dbo.calificaciones (periodo_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_calificaciones_finales_materia' AND object_id = OBJECT_ID(N'dbo.calificaciones_finales'))
    CREATE INDEX IX_calificaciones_finales_materia ON dbo.calificaciones_finales (materia_id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_alertas_matricula' AND object_id = OBJECT_ID(N'dbo.alertas'))
    CREATE INDEX IX_alertas_matricula ON dbo.alertas (matricula_id);
GO

IF COL_LENGTH(N'dbo.estudiantes', N'fecha_nacimiento') IS NULL
    ALTER TABLE dbo.estudiantes ADD fecha_nacimiento DATE NULL;
GO

IF COL_LENGTH(N'dbo.estudiantes', N'curso') IS NULL
    ALTER TABLE dbo.estudiantes ADD curso NVARCHAR(100) NULL;
GO

IF COL_LENGTH(N'dbo.estudiantes', N'telefono') IS NULL
    ALTER TABLE dbo.estudiantes ADD telefono NVARCHAR(20) NULL;
GO

IF COL_LENGTH(N'dbo.estudiantes', N'tutor') IS NULL
    ALTER TABLE dbo.estudiantes ADD tutor NVARCHAR(150) NULL;
GO

IF COL_LENGTH(N'dbo.estudiantes', N'direccion') IS NULL
    ALTER TABLE dbo.estudiantes ADD direccion NVARCHAR(250) NULL;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_estudiantes_curso' AND object_id = OBJECT_ID(N'dbo.estudiantes'))
    CREATE INDEX IX_estudiantes_curso ON dbo.estudiantes (curso);
GO

IF NOT EXISTS (SELECT 1 FROM dbo.periodos)
    INSERT INTO dbo.periodos (nombre) VALUES (N'P1 - Primer Periodo'), (N'P2 - Segundo Periodo'), (N'P3 - Tercer Periodo');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.materias)
    INSERT INTO dbo.materias (nombre) VALUES (N'Desarrollo de Aplicaciones Web'), (N'Bases de Datos Relacionales'), (N'Matemática Aplicada');
GO
