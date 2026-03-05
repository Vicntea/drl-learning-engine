-- Alterar tabla profesores para agregar región y tipo usuario
ALTER TABLE IF EXISTS escuela_template.profesores
    ADD COLUMN IF NOT EXISTS region_id INTEGER REFERENCES public.regiones_chile(id);
ALTER TABLE IF EXISTS escuela_template.profesores
    ADD COLUMN IF NOT EXISTS tipo_usuario_id INTEGER REFERENCES public.tipos_usuario(id);

-- Alterar tabla alumnos para agregar región y tipo usuario
ALTER TABLE IF EXISTS escuela_template.alumnos
    ADD COLUMN IF NOT EXISTS region_id INTEGER REFERENCES public.regiones_chile(id);
ALTER TABLE IF EXISTS escuela_template.alumnos
    ADD COLUMN IF NOT EXISTS tipo_usuario_id INTEGER REFERENCES public.tipos_usuario(id);
-- ============================================
-- ENUMS Y TABLAS DE REFERENCIA (CHILE Y EDUCACIÓN MUSICAL)
-- ============================================

CREATE TABLE IF NOT EXISTS public.regiones_chile (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);
INSERT INTO public.regiones_chile (nombre) VALUES
('Arica y Parinacota'), ('Tarapacá'), ('Antofagasta'), ('Atacama'), ('Coquimbo'),
('Valparaíso'), ('Metropolitana de Santiago'), ('Libertador General Bernardo O’Higgins'),
('Maule'), ('Ñuble'), ('Biobío'), ('La Araucanía'), ('Los Ríos'), ('Los Lagos'),
('Aysén del General Carlos Ibáñez del Campo'), ('Magallanes y de la Antártica Chilena')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS public.tipos_usuario (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);
INSERT INTO public.tipos_usuario (nombre) VALUES ('admin'), ('profesor'), ('alumno'), ('apoderado') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS public.tipos_ejercicio (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);
INSERT INTO public.tipos_ejercicio (nombre, descripcion) VALUES
('Teoría', 'Ejercicios de teoría musical'),
('Ritmo', 'Ejercicios de ritmo'),
('Melodía', 'Ejercicios de melodía'),
('Armonía', 'Ejercicios de armonía'),
('Dictado', 'Dictado musical'),
('Lectura', 'Lectura musical'),
('Instrumento', 'Práctica instrumental')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS public.niveles_dificultad (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);
INSERT INTO public.niveles_dificultad (nombre, descripcion) VALUES
('Inicial', 'Nivel básico'),
('Intermedio', 'Nivel medio'),
('Avanzado', 'Nivel avanzado')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS public.tipos_feedback (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);
INSERT INTO public.tipos_feedback (nombre, descripcion) VALUES
('Motivacional', 'Feedback para motivar al alumno'),
('Correctivo', 'Feedback para corregir errores'),
('Refuerzo', 'Feedback de refuerzo positivo'),
('Sugerencia', 'Sugerencias de mejora')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS public.tipos_logro (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);
INSERT INTO public.tipos_logro (nombre, descripcion) VALUES
('Primer ejercicio', 'Completó su primer ejercicio'),
('Constancia', 'Completó 7 días seguidos'),
('Maestro del ritmo', 'Alto rendimiento en ejercicios de ritmo'),
('Teórico experto', 'Alto rendimiento en teoría musical'),
('Superación', 'Mejoró su rendimiento notablemente')
ON CONFLICT DO NOTHING;

-- ============================================
-- SCHEMA Y TABLAS TEMPLATE MULTI-TENANT
-- ============================================

CREATE SCHEMA IF NOT EXISTS escuela_template;

CREATE TABLE IF NOT EXISTS escuela_template.profesores (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    region_id INTEGER REFERENCES public.regiones_chile(id),
    tipo_usuario_id INTEGER REFERENCES public.tipos_usuario(id),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.alumnos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    region_id INTEGER REFERENCES public.regiones_chile(id),
    tipo_usuario_id INTEGER REFERENCES public.tipos_usuario(id),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.cursos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.tareas (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER,
    titulo TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.ia_config (
    id SERIAL PRIMARY KEY,
    modelo_version TEXT NOT NULL,
    parametros JSONB,
    fecha_desde TIMESTAMP DEFAULT now(),
    fecha_hasta TIMESTAMP,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.ejercicios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    dificultad_id INTEGER REFERENCES public.niveles_dificultad(id),
    tipo_id INTEGER REFERENCES public.tipos_ejercicio(id),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.resultados (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    ejercicio_id INTEGER NOT NULL,
    score NUMERIC,
    fecha TIMESTAMP DEFAULT now(),
    detalles JSONB,
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE,
    FOREIGN KEY (ejercicio_id) REFERENCES escuela_template.ejercicios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS escuela_template.logs_actividad (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT now(),
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS escuela_template.logs_ia (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER,
    ejercicio_id INTEGER,
    ia_config_id INTEGER,
    accion TEXT NOT NULL,
    parametros JSONB,
    resultado JSONB,
    fecha TIMESTAMP DEFAULT now(),
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE SET NULL,
    FOREIGN KEY (ejercicio_id) REFERENCES escuela_template.ejercicios(id) ON DELETE SET NULL,
    FOREIGN KEY (ia_config_id) REFERENCES escuela_template.ia_config(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS escuela_template.rendimiento (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    concepto TEXT NOT NULL,
    nivel NUMERIC,
    fecha TIMESTAMP DEFAULT now(),
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS escuela_template.sesiones_practica (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    inicio TIMESTAMP DEFAULT now(),
    fin TIMESTAMP,
    metadata JSONB,
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS escuela_template.feedback_ia (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    ejercicio_id INTEGER,
    tipo_feedback_id INTEGER REFERENCES public.tipos_feedback(id),
    mensaje TEXT,
    fecha TIMESTAMP DEFAULT now(),
    metadata JSONB,
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE,
    FOREIGN KEY (ejercicio_id) REFERENCES escuela_template.ejercicios(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS escuela_template.logros (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    tipo_logro_id INTEGER REFERENCES public.tipos_logro(id),
    fecha TIMESTAMP DEFAULT now(),
    metadata JSONB,
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE
);

-- ============================================
-- FUNCION ROBUSTA PARA CREAR INSTITUCION Y CLONAR TABLAS
-- ============================================

CREATE TABLE IF NOT EXISTS public.instituciones (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    schema_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT now(),
    activo BOOLEAN DEFAULT true
);

DROP FUNCTION IF EXISTS public.crear_institucion(TEXT, TEXT);
CREATE OR REPLACE FUNCTION public.crear_institucion(
    nombre_institucion TEXT,
    schema_nuevo TEXT
)
RETURNS VOID AS $$
DECLARE
    _sql TEXT;
BEGIN
    INSERT INTO public.instituciones(nombre, schema_name)
    VALUES (nombre_institucion, schema_nuevo);
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.profesores AS TABLE escuela_template.profesores WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.alumnos AS TABLE escuela_template.alumnos WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.cursos AS TABLE escuela_template.cursos WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.tareas AS TABLE escuela_template.tareas WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.ia_config AS TABLE escuela_template.ia_config WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.ejercicios AS TABLE escuela_template.ejercicios WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.resultados AS TABLE escuela_template.resultados WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.logs_actividad AS TABLE escuela_template.logs_actividad WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.logs_ia AS TABLE escuela_template.logs_ia WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.rendimiento AS TABLE escuela_template.rendimiento WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.sesiones_practica AS TABLE escuela_template.sesiones_practica WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.feedback_ia AS TABLE escuela_template.feedback_ia WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.logros AS TABLE escuela_template.logros WITH NO DATA', schema_nuevo);
END;
$$ LANGUAGE plpgsql;
);
INSERT INTO public.regiones_chile (nombre) VALUES
('Arica y Parinacota'), ('Tarapacá'), ('Antofagasta'), ('Atacama'), ('Coquimbo'),
('Valparaíso'), ('Metropolitana de Santiago'), ('Libertador General Bernardo O’Higgins'),
('Maule'), ('Ñuble'), ('Biobío'), ('La Araucanía'), ('Los Ríos'), ('Los Lagos'),
('Aysén del General Carlos Ibáñez del Campo'), ('Magallanes y de la Antártica Chilena')
ON CONFLICT DO NOTHING;

-- Tipos de usuario
CREATE TABLE IF NOT EXISTS public.tipos_usuario (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);
INSERT INTO public.tipos_usuario (nombre) VALUES ('admin'), ('profesor'), ('alumno'), ('apoderado') ON CONFLICT DO NOTHING;

-- Tipos de ejercicio musical
CREATE TABLE IF NOT EXISTS public.tipos_ejercicio (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);
INSERT INTO public.tipos_ejercicio (nombre, descripcion) VALUES
('Teoría', 'Ejercicios de teoría musical'),
('Ritmo', 'Ejercicios de ritmo'),
('Melodía', 'Ejercicios de melodía'),
('Armonía', 'Ejercicios de armonía'),
('Dictado', 'Dictado musical'),
('Lectura', 'Lectura musical'),
('Instrumento', 'Práctica instrumental')
ON CONFLICT DO NOTHING;

-- Niveles de dificultad
CREATE TABLE IF NOT EXISTS public.niveles_dificultad (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);
INSERT INTO public.niveles_dificultad (nombre, descripcion) VALUES
('Inicial', 'Nivel básico'),
('Intermedio', 'Nivel medio'),
('Avanzado', 'Nivel avanzado')
ON CONFLICT DO NOTHING;

-- Tipos de feedback IA
CREATE TABLE IF NOT EXISTS public.tipos_feedback (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);
INSERT INTO public.tipos_feedback (nombre, descripcion) VALUES
('Motivacional', 'Feedback para motivar al alumno'),
('Correctivo', 'Feedback para corregir errores'),
('Refuerzo', 'Feedback de refuerzo positivo'),
('Sugerencia', 'Sugerencias de mejora')
ON CONFLICT DO NOTHING;

-- Tipos de logros/badges
CREATE TABLE IF NOT EXISTS public.tipos_logro (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);
INSERT INTO public.tipos_logro (nombre, descripcion) VALUES
('Primer ejercicio', 'Completó su primer ejercicio'),
('Constancia', 'Completó 7 días seguidos'),
('Maestro del ritmo', 'Alto rendimiento en ejercicios de ritmo'),
('Teórico experto', 'Alto rendimiento en teoría musical'),
('Superación', 'Mejoró su rendimiento notablemente')
ON CONFLICT DO NOTHING;

-- ============================================
-- 7️⃣ TABLAS EXTRA EN ESCUELA_TEMPLATE PARA MULTI-TENANT IA DRL
-- ============================================

-- Configuración y versión de IA usada por la escuela
CREATE TABLE IF NOT EXISTS escuela_template.ia_config (
    id SERIAL PRIMARY KEY,
    modelo_version TEXT NOT NULL,
    parametros JSONB,
    fecha_desde TIMESTAMP DEFAULT now(),
    fecha_hasta TIMESTAMP,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now()
);

-- Ejercicios musicales disponibles en la escuela
CREATE TABLE IF NOT EXISTS escuela_template.ejercicios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    dificultad_id INTEGER REFERENCES public.niveles_dificultad(id),
    tipo_id INTEGER REFERENCES public.tipos_ejercicio(id),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- Resultados de ejercicios por alumno
CREATE TABLE IF NOT EXISTS escuela_template.resultados (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    ejercicio_id INTEGER NOT NULL,
    score NUMERIC,
    fecha TIMESTAMP DEFAULT now(),
    detalles JSONB,
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE,
    FOREIGN KEY (ejercicio_id) REFERENCES escuela_template.ejercicios(id) ON DELETE CASCADE
);

-- Logs de actividad de alumnos y profesores
CREATE TABLE IF NOT EXISTS escuela_template.logs_actividad (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT now(),
    metadata JSONB
);

-- Logs de decisiones de la IA (auditoría)
CREATE TABLE IF NOT EXISTS escuela_template.logs_ia (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER,
    ejercicio_id INTEGER,
    ia_config_id INTEGER,
    accion TEXT NOT NULL,
    parametros JSONB,
    resultado JSONB,
    fecha TIMESTAMP DEFAULT now(),
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE SET NULL,
    FOREIGN KEY (ejercicio_id) REFERENCES escuela_template.ejercicios(id) ON DELETE SET NULL,
    FOREIGN KEY (ia_config_id) REFERENCES escuela_template.ia_config(id) ON DELETE SET NULL
);

-- Progreso/rendimiento de alumnos por concepto musical
CREATE TABLE IF NOT EXISTS escuela_template.rendimiento (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    concepto TEXT NOT NULL,
    nivel NUMERIC,
    fecha TIMESTAMP DEFAULT now(),
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE
);


-- ============================================
-- 8️⃣ EXTENDER FUNCION PARA CREAR INSTITUCION (ROBUSTA Y ORDENADA)
-- ============================================

DROP FUNCTION IF EXISTS public.crear_institucion(TEXT, TEXT);
CREATE OR REPLACE FUNCTION public.crear_institucion(
    nombre_institucion TEXT,
    schema_nuevo TEXT
)
RETURNS VOID AS $$
DECLARE
    _sql TEXT;
BEGIN
    -- Insertar institución
    INSERT INTO public.instituciones(nombre, schema_name)
    VALUES (nombre_institucion, schema_nuevo);

    -- Crear schema
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', schema_nuevo);

    -- Crear tablas en orden correcto (sin constraints primero)
    EXECUTE format('CREATE TABLE %I.profesores AS TABLE escuela_template.profesores WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.alumnos AS TABLE escuela_template.alumnos WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.cursos AS TABLE escuela_template.cursos WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.tareas AS TABLE escuela_template.tareas WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.ia_config AS TABLE escuela_template.ia_config WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.ejercicios AS TABLE escuela_template.ejercicios WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.resultados AS TABLE escuela_template.resultados WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.logs_actividad AS TABLE escuela_template.logs_actividad WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.logs_ia AS TABLE escuela_template.logs_ia WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.rendimiento AS TABLE escuela_template.rendimiento WITH NO DATA', schema_nuevo);

    -- Agregar constraints y claves foráneas después (evita errores de dependencia)
    -- Ejemplo para resultados
    _sql := format('ALTER TABLE %I.resultados ADD CONSTRAINT fk_alumno FOREIGN KEY (alumno_id) REFERENCES %I.alumnos(id) ON DELETE CASCADE', schema_nuevo, schema_nuevo);
    EXECUTE _sql;
    _sql := format('ALTER TABLE %I.resultados ADD CONSTRAINT fk_ejercicio FOREIGN KEY (ejercicio_id) REFERENCES %I.ejercicios(id) ON DELETE CASCADE', schema_nuevo, schema_nuevo);
    EXECUTE _sql;
    -- Ejemplo para logs_ia
    _sql := format('ALTER TABLE %I.logs_ia ADD CONSTRAINT fk_ia_alumno FOREIGN KEY (alumno_id) REFERENCES %I.alumnos(id) ON DELETE SET NULL', schema_nuevo);
    EXECUTE _sql;
    _sql := format('ALTER TABLE %I.logs_ia ADD CONSTRAINT fk_ia_ejercicio FOREIGN KEY (ejercicio_id) REFERENCES %I.ejercicios(id) ON DELETE SET NULL', schema_nuevo);
    EXECUTE _sql;
    _sql := format('ALTER TABLE %I.logs_ia ADD CONSTRAINT fk_ia_config FOREIGN KEY (ia_config_id) REFERENCES %I.ia_config(id) ON DELETE SET NULL', schema_nuevo);
    EXECUTE _sql;
    -- Ejemplo para rendimiento
    _sql := format('ALTER TABLE %I.rendimiento ADD CONSTRAINT fk_rend_alumno FOREIGN KEY (alumno_id) REFERENCES %I.alumnos(id) ON DELETE CASCADE', schema_nuevo);
    EXECUTE _sql;

    -- Puedes agregar más constraints aquí según agregues más tablas
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 10️⃣ MÁS TABLAS ÚTILES PARA EDUCACIÓN MUSICAL CON IA
-- ============================================

-- Tabla de sesiones de práctica
CREATE TABLE IF NOT EXISTS escuela_template.sesiones_practica (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    inicio TIMESTAMP DEFAULT now(),
    fin TIMESTAMP,
    metadata JSONB,
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE
);

-- Tabla de feedback de IA a alumnos
CREATE TABLE IF NOT EXISTS escuela_template.feedback_ia (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    ejercicio_id INTEGER,
    tipo_feedback_id INTEGER REFERENCES public.tipos_feedback(id),
    mensaje TEXT,
    fecha TIMESTAMP DEFAULT now(),
    metadata JSONB,
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE,
    FOREIGN KEY (ejercicio_id) REFERENCES escuela_template.ejercicios(id) ON DELETE SET NULL
);

-- Tabla de logros/badges
CREATE TABLE IF NOT EXISTS escuela_template.logros (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL,
    tipo_logro_id INTEGER REFERENCES public.tipos_logro(id),
    fecha TIMESTAMP DEFAULT now(),
    metadata JSONB,
    FOREIGN KEY (alumno_id) REFERENCES escuela_template.alumnos(id) ON DELETE CASCADE
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_resultados_alumno ON escuela_template.resultados(alumno_id);
CREATE INDEX IF NOT EXISTS idx_resultados_ejercicio ON escuela_template.resultados(ejercicio_id);
CREATE INDEX IF NOT EXISTS idx_logs_actividad_usuario ON escuela_template.logs_actividad(usuario_id);
CREATE INDEX IF NOT EXISTS idx_logs_ia_alumno ON escuela_template.logs_ia(alumno_id);
CREATE INDEX IF NOT EXISTS idx_rendimiento_alumno ON escuela_template.rendimiento(alumno_id);

-- ============================================
-- 11️⃣ MÁS TRIGGERS ÚTILES (EJEMPLOS)
-- ============================================

-- Trigger para loguear inserciones de resultados
CREATE OR REPLACE FUNCTION escuela_template.log_resultado_insert() RETURNS trigger AS $$
BEGIN
    INSERT INTO escuela_template.logs_actividad(usuario_id, tipo, descripcion, fecha, metadata)
    VALUES (NEW.alumno_id, 'insert_resultado', 'Nuevo resultado registrado', now(), row_to_json(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS resultado_insert_trigger ON escuela_template.resultados;
CREATE TRIGGER resultado_insert_trigger
AFTER INSERT ON escuela_template.resultados
FOR EACH ROW EXECUTE FUNCTION escuela_template.log_resultado_insert();

-- ============================================
-- 9️⃣ TRIGGERS DE AUDITORÍA (EJEMPLO BÁSICO)
-- ============================================

-- Ejemplo: trigger para loguear cambios en alumnos
CREATE OR REPLACE FUNCTION escuela_template.log_alumno_update() RETURNS trigger AS $$
BEGIN
    INSERT INTO escuela_template.logs_actividad(usuario_id, tipo, descripcion, fecha, metadata)
    VALUES (NEW.usuario_id, 'update_alumno', 'Actualización de alumno', now(), row_to_json(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS alumno_update_trigger ON escuela_template.alumnos;
CREATE TRIGGER alumno_update_trigger
AFTER UPDATE ON escuela_template.alumnos
FOR EACH ROW EXECUTE FUNCTION escuela_template.log_alumno_update();

-- ============================================
-- 2️⃣ TABLAS GLOBALES (AUTH EN PUBLIC)
-- ============================================

CREATE TABLE IF NOT EXISTS public.instituciones (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    schema_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT now(),
    activo BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS public.usuarios (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    institucion_id INTEGER NOT NULL REFERENCES public.instituciones(id) ON DELETE CASCADE,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.roles (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS public.permisos (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS public.usuario_roles (
    usuario_id INTEGER REFERENCES public.usuarios(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES public.roles(id) ON DELETE CASCADE,
    PRIMARY KEY (usuario_id, role_id)
);

CREATE TABLE IF NOT EXISTS public.role_permisos (
    role_id INTEGER REFERENCES public.roles(id) ON DELETE CASCADE,
    permiso_id INTEGER REFERENCES public.permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permiso_id)
);

-- ============================================
-- 3️⃣ DATOS INICIALES RBAC
-- ============================================

INSERT INTO public.roles (nombre)
VALUES ('admin'), ('profesor'), ('alumno')
ON CONFLICT DO NOTHING;

INSERT INTO public.permisos (nombre)
VALUES 
('ver_cursos'),
('crear_curso'),
('editar_curso'),
('crear_tarea'),
('editar_tarea'),
('ver_notas')
ON CONFLICT DO NOTHING;

-- Admin tiene todos los permisos
INSERT INTO public.role_permisos
SELECT r.id, p.id
FROM public.roles r
CROSS JOIN public.permisos p
WHERE r.nombre = 'admin'
ON CONFLICT DO NOTHING;

-- ============================================
-- 4️⃣ TEMPLATE DE ESCUELA
-- ============================================

CREATE SCHEMA IF NOT EXISTS escuela_template;

CREATE TABLE IF NOT EXISTS escuela_template.profesores (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.alumnos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.cursos (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS escuela_template.tareas (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER,
    titulo TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

-- ============================================
-- 5️⃣ FUNCION PARA CREAR NUEVA INSTITUCION
-- ============================================

CREATE OR REPLACE FUNCTION public.crear_institucion(
    nombre_institucion TEXT,
    schema_nuevo TEXT
)
RETURNS VOID AS $$
BEGIN

    -- Insertar institución
    INSERT INTO public.instituciones(nombre, schema_name)
    VALUES (nombre_institucion, schema_nuevo);

    -- Crear schema
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', schema_nuevo);

    -- Clonar tablas desde template
    EXECUTE format('CREATE TABLE %I.profesores AS TABLE escuela_template.profesores WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.alumnos AS TABLE escuela_template.alumnos WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.cursos AS TABLE escuela_template.cursos WITH NO DATA', schema_nuevo);
    EXECUTE format('CREATE TABLE %I.tareas AS TABLE escuela_template.tareas WITH NO DATA', schema_nuevo);

END;
$$ LANGUAGE plpgsql;

