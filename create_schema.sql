-- ================================================
-- SCHEMA PARA DRL LEARNING ENGINE INTEGRATION
-- Ejecutar esto en Supabase SQL Editor
-- ================================================

-- 1. TABLA: ESTUDIANTES
CREATE TABLE IF NOT EXISTS students (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Índice para búsquedas rápidas
CREATE INDEX idx_students_user_id ON students(user_id);

-- ================================================
-- 2. TABLA: PROFICIENCIAS (Habilidades por Nodo)
-- ================================================

CREATE TABLE IF NOT EXISTS proficiencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES students(id) ON DELETE CASCADE NOT NULL,
  node TEXT NOT NULL,
  proficiency_level FLOAT NOT NULL DEFAULT 0.0,
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(student_id, node)
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_proficiencies_student ON proficiencies(student_id);
CREATE INDEX idx_proficiencies_node ON proficiencies(node);

-- ================================================
-- 3. TABLA: SESIONES
-- ================================================

CREATE TABLE IF NOT EXISTS sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES students(id) ON DELETE CASCADE NOT NULL,
  total_reward FLOAT NOT NULL DEFAULT 0.0,
  node_rewards JSONB NOT NULL DEFAULT '{}'::jsonb,
  success_rate FLOAT NOT NULL DEFAULT 0.0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_sessions_student ON sessions(student_id);
CREATE INDEX idx_sessions_created ON sessions(created_at);

-- ================================================
-- 4. TABLA: EVENTOS DE SESIÓN
-- ================================================

CREATE TABLE IF NOT EXISTS session_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(id) ON DELETE CASCADE NOT NULL,
  node TEXT NOT NULL,
  correct BOOLEAN NOT NULL,
  difficulty INT NOT NULL,
  response_time INT NOT NULL,
  reward FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_session_events_session ON session_events(session_id);
CREATE INDEX idx_session_events_node ON session_events(node);

-- ================================================
-- 5. TABLA: USUARIOS (ROLES)
-- ================================================

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'teacher', 'admin')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Índice para búsquedas por role
CREATE INDEX idx_users_role ON users(role);

-- ================================================
-- 6. POLÍTICAS DE SEGURIDAD (RLS)
-- ================================================

-- Habilitar RLS en todas las tablas
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE proficiencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- POLÍTICA: Students - Los estudiantes solo ven sus propios datos
CREATE POLICY "Students can view own data"
  ON students FOR SELECT
  USING (auth.uid() = user_id);

-- POLÍTICA: Proficiencies - Acceso a propias proficiencias
CREATE POLICY "Students can view own proficiencies"
  ON proficiencies FOR SELECT
  USING (
    student_id IN (
      SELECT id FROM students WHERE user_id = auth.uid()
    )
  );

-- POLÍTICA: Sessions - Acceso a propias sesiones
CREATE POLICY "Students can view own sessions"
  ON sessions FOR SELECT
  USING (
    student_id IN (
      SELECT id FROM students WHERE user_id = auth.uid()
    )
  );

-- POLÍTICA: SessionEvents - Acceso a eventos propios
CREATE POLICY "Students can view own session events"
  ON session_events FOR SELECT
  USING (
    session_id IN (
      SELECT id FROM sessions 
      WHERE student_id IN (
        SELECT id FROM students WHERE user_id = auth.uid()
      )
    )
  );

-- ================================================
-- 7. VISTAS ÚTILES
-- ================================================

-- Vista: Estadísticas por estudiante
CREATE OR REPLACE VIEW student_stats AS
SELECT 
  s.id,
  s.user_id,
  s.name,
  COUNT(DISTINCT ss.id) as total_sessions,
  ROUND(AVG(ss.total_reward)::numeric, 2) as avg_reward,
  ROUND(AVG(ss.success_rate)::numeric, 3) as avg_success_rate,
  MAX(ss.created_at) as last_session
FROM students s
LEFT JOIN sessions ss ON s.id = ss.student_id
GROUP BY s.id, s.user_id, s.name;

-- Vista: Proficiencias actuales
CREATE OR REPLACE VIEW current_proficiencies AS
SELECT 
  student_id,
  node,
  proficiency_level,
  updated_at
FROM proficiencies
ORDER BY student_id, node;

-- ================================================
-- 8. FUNCIONES AUXILIARES
-- ================================================

-- Función: Obtener promedio de proficiencia
CREATE OR REPLACE FUNCTION get_avg_proficiency(p_student_id UUID)
RETURNS FLOAT AS $$
  SELECT AVG(proficiency_level)::FLOAT
  FROM proficiencies
  WHERE student_id = p_student_id;
$$ LANGUAGE SQL;

-- Función: Obtener nodos débiles (proficiencia < 0.5)
CREATE OR REPLACE FUNCTION get_weak_nodes(p_student_id UUID)
RETURNS TABLE(node TEXT, proficiency_level FLOAT) AS $$
  SELECT node, proficiency_level
  FROM proficiencies
  WHERE student_id = p_student_id AND proficiency_level < 0.5
  ORDER BY proficiency_level ASC;
$$ LANGUAGE SQL;

-- ================================================
-- 9. SEED DATA (Opcional - para testing)
-- ================================================

-- Insertar roles de usuario de prueba (comentado por seguridad)
-- INSERT INTO users (id, email, role)
-- VALUES (gen_random_uuid(), 'teacher@example.com', 'teacher')
-- ON CONFLICT (email) DO NOTHING;

-- ================================================
-- 10. TRIGGERS (Opcional - para auditoría)
-- ================================================

-- Trigger: Actualizar updated_at en students
CREATE OR REPLACE FUNCTION update_students_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_students_updated_at
BEFORE UPDATE ON students
FOR EACH ROW
EXECUTE FUNCTION update_students_updated_at();

-- Trigger: Actualizar updated_at en users
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_users_updated_at();

-- ================================================
-- PERMISO ESPECIAL: Backend puede escribir en todas las tablas
-- Esto se aplica usando SUPABASE_SERVICE_ROLE_KEY
-- ================================================

-- No hay restricción RLS para el service role (tiene permisos totales)
-- Las políticas de RLS solo afectan a usuarios normales (con JWT)
