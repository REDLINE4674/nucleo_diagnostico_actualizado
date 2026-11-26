-- =========================================================
-- Script SQL para PostgreSQL - Núcleo de Diagnóstico
-- Tablas: medicamento y consulta
-- =========================================================

-- 1. Tabla medicamento
CREATE TABLE IF NOT EXISTS medicamento (
    id_medicamento SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    fecha_caducidad DATE NOT NULL,
    presentacion VARCHAR(100) NOT NULL,
    via_de_administracion VARCHAR(80) NOT NULL
);

-- 2. Tabla consulta
CREATE TABLE IF NOT EXISTS consulta (
    id_consulta SERIAL PRIMARY KEY,
    id_cita INTEGER NOT NULL,
    diagnostico TEXT NOT NULL,
    id_medicamento INTEGER NULL,
    CONSTRAINT fk_consulta_cita
        FOREIGN KEY (id_cita)
        REFERENCES cita (id_cita)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_consulta_medicamento
        FOREIGN KEY (id_medicamento)
        REFERENCES medicamento (id_medicamento)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


