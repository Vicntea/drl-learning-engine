-- ================================================
-- DRL LEARNING ENGINE - SCHEMA COMPLETO
-- Schema: drl_testing
-- ================================================

-- EXTENSION
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ================================================
-- 0. SCHEMA
-- ================================================

CREATE SCHEMA IF NOT EXISTS drl_testing;

-- ================================================
-- 1. USERS (ROLES)
-- ================================================

CREATE TABLE IF NOT EXISTS drl_testing.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL DEFAULT 'student'
    CHECK (role IN ('student', 'teacher', 'admin')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_role
ON drl_testing.users(role);

-- ================================================
-- 2. STUDENTS
-- ================================================

CREATE TABLE IF NOT EXISTS drl_testing.students (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES drl_testing.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_students_user_id
ON drl_testing.students(user_id);

-- ================================================
-- 3. PROFIENCY (DRL STATE JSONB)
-- ================================================

CREATE TABLE IF NOT EXISTS drl_testing.student_proficiency (
  student_id UUID PRIMARY KEY REFERENCES drl_testing.students(id) ON DELETE CASCADE,
  skill_proficiency JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_student_proficiency_gin
ON drl_testing.student_proficiency
USING GIN (skill_proficiency);

-- ================================================
-- 4. DRL SESSIONS (EPISODIOS)
-- ================================================

CREATE TABLE IF NOT EXISTS drl_testing.sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES drl_testing.students(id) ON DELETE CASCADE NOT NULL,

  total_reward FLOAT NOT NULL DEFAULT 0.0,
  node_rewards JSONB NOT NULL DEFAULT '{}'::jsonb,
  success_rate FLOAT NOT NULL DEFAULT 0.0,

  started_at TIMESTAMP DEFAULT NOW(),
  ended_at TIMESTAMP,

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sessions_student
ON drl_testing.sessions(student_id);

CREATE INDEX IF NOT EXISTS idx_sessions_created
ON drl_testing.sessions(created_at);

-- ================================================
-- 5. SESSION EVENTS (STEP REWARD LOG)
-- ================================================

CREATE TABLE IF NOT EXISTS drl_testing.session_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES drl_testing.sessions(id) ON DELETE CASCADE NOT NULL,

  node TEXT NOT NULL,
  correct BOOLEAN NOT NULL,
  difficulty INT NOT NULL,
  response_time INT NOT NULL,
  reward FLOAT,

  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_events_session
ON drl_testing.session_events(session_id);

CREATE INDEX IF NOT EXISTS idx_session_events_node
ON drl_testing.session_events(node);

-- ================================================
-- 6. USER ACTIVITY (LOGIN / LOGOUT)
-- ================================================

CREATE TABLE IF NOT EXISTS drl_testing.user_activity_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id UUID REFERENCES drl_testing.students(id) ON DELETE CASCADE NOT NULL,

  login_at TIMESTAMP DEFAULT NOW(),
  logout_at TIMESTAMP,

  duration_seconds INT,
  active BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_activity_student
ON drl_testing.user_activity_sessions(student_id);

CREATE INDEX IF NOT EXISTS idx_activity_active
ON drl_testing.user_activity_sessions(active);

-- ================================================
-- 7. VIEW: ESTADÍSTICAS
-- ================================================

CREATE OR REPLACE VIEW drl_testing.student_stats AS
SELECT 
  s.id,
  s.user_id,
  s.name,
  COUNT(DISTINCT ss.id) AS total_sessions,
  ROUND(AVG(ss.total_reward)::numeric, 2) AS avg_reward,
  ROUND(AVG(ss.success_rate)::numeric, 3) AS avg_success_rate,
  MAX(ss.created_at) AS last_session
FROM drl_testing.students s
LEFT JOIN drl_testing.sessions ss ON s.id = ss.student_id
GROUP BY s.id, s.user_id, s.name;

-- ================================================
-- 8. FUNCTIONS (DRL HELPERS)
-- ================================================

CREATE OR REPLACE FUNCTION drl_testing.get_avg_proficiency(p_student_id UUID)
RETURNS FLOAT AS $$
  SELECT COALESCE(AVG((value)::float), 0)
  FROM drl_testing.student_proficiency,
  jsonb_each_text(skill_proficiency)
  WHERE student_id = p_student_id;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION drl_testing.get_weak_nodes(p_student_id UUID)
RETURNS TABLE(node TEXT, proficiency FLOAT) AS $$
  SELECT key, (value)::float
  FROM drl_testing.student_proficiency,
  jsonb_each_text(skill_proficiency)
  WHERE student_id = p_student_id
    AND (value)::float < 0.5
  ORDER BY (value)::float ASC;
$$ LANGUAGE SQL;

-- ================================================
-- 9. UPDATED_AT TRIGGERS
-- ================================================

CREATE OR REPLACE FUNCTION drl_testing.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_students_updated
BEFORE UPDATE ON drl_testing.students
FOR EACH ROW EXECUTE FUNCTION drl_testing.update_timestamp();

CREATE TRIGGER trg_users_updated
BEFORE UPDATE ON drl_testing.users
FOR EACH ROW EXECUTE FUNCTION drl_testing.update_timestamp();

CREATE TRIGGER trg_proficiency_updated
BEFORE UPDATE ON drl_testing.student_proficiency
FOR EACH ROW EXECUTE FUNCTION drl_testing.update_timestamp();

-- ================================================
-- 10. RLS (SEGURIDAD SUPABASE)
-- ================================================

ALTER TABLE drl_testing.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE drl_testing.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE drl_testing.student_proficiency ENABLE ROW LEVEL SECURITY;
ALTER TABLE drl_testing.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE drl_testing.session_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE drl_testing.user_activity_sessions ENABLE ROW LEVEL SECURITY;

-- USERS
CREATE POLICY "Users can read own data"
ON drl_testing.users FOR SELECT
USING (auth.uid() = id);

-- STUDENTS
CREATE POLICY "Students can view own data"
ON drl_testing.students FOR SELECT
USING (auth.uid() = user_id);

-- PROFIENCY
CREATE POLICY "Students can view own proficiency"
ON drl_testing.student_proficiency FOR SELECT
USING (
  student_id IN (
    SELECT id FROM drl_testing.students WHERE user_id = auth.uid()
  )
);

-- SESSIONS
CREATE POLICY "Students can view own sessions"
ON drl_testing.sessions FOR SELECT
USING (
  student_id IN (
    SELECT id FROM drl_testing.students WHERE user_id = auth.uid()
  )
);

-- EVENTS
CREATE POLICY "Students can view own events"
ON drl_testing.session_events FOR SELECT
USING (
  session_id IN (
    SELECT id FROM drl_testing.sessions
    WHERE student_id IN (
      SELECT id FROM drl_testing.students WHERE user_id = auth.uid()
    )
  )
);

-- ACTIVITY
CREATE POLICY "Students can view own activity"
ON drl_testing.user_activity_sessions FOR SELECT
USING (
  student_id IN (
    SELECT id FROM drl_testing.students WHERE user_id = auth.uid()
  )
);

-- ================================================
-- FIN
-- ================================================