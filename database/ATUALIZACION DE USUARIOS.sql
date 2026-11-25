-- =========================================================
-- Actualización de la tabla public.usuarios
-- Vinculación con empleado y doctor + restricción de exclusión
-- =========================================================

ALTER TABLE public.usuarios
    ADD COLUMN IF NOT EXISTS id_empleado INTEGER,
    ADD COLUMN IF NOT EXISTS id_doctor INTEGER;

DO $$
BEGIN
    -- 1. Llave foránea hacia public.empleado
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'usuarios_id_empleado_fkey'
          AND conrelid = 'public.usuarios'::regclass
    ) THEN
        ALTER TABLE public.usuarios
            ADD CONSTRAINT usuarios_id_empleado_fkey
            FOREIGN KEY (id_empleado)
            REFERENCES public.empleado (id_empleado)
            ON UPDATE CASCADE
            ON DELETE SET NULL;
    END IF;

    -- 2. Llave foránea hacia public.doctor
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'usuarios_id_doctor_fkey'
          AND conrelid = 'public.usuarios'::regclass
    ) THEN
        ALTER TABLE public.usuarios
            ADD CONSTRAINT usuarios_id_doctor_fkey
            FOREIGN KEY (id_doctor)
            REFERENCES public.doctor (id_doctor)
            ON UPDATE CASCADE
            ON DELETE SET NULL;
    END IF;

    -- 3. Restricción CHECK: un usuario no puede ser empleado y doctor a la vez
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'usuarios_empleado_o_doctor_chk'
          AND conrelid = 'public.usuarios'::regclass
    ) THEN
        ALTER TABLE public.usuarios
            ADD CONSTRAINT usuarios_empleado_o_doctor_chk
            CHECK (NOT (id_empleado IS NOT NULL AND id_doctor IS NOT NULL));
    END IF;
END
$$;