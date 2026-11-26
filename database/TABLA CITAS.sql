CREATE TABLE Cita (    id_cita INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_paciente INTEGER NOT NULL,
    id_medico INTEGER NOT NULL,
    hora TIME NOT NULL,
    fecha DATE NOT NULL,

    CONSTRAINT fk_cita_paciente
        FOREIGN KEY (id_paciente)
        REFERENCES "Paciente"(codigo)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_cita_medico
        FOREIGN KEY (id_medico)
        REFERENCES "Doctor"(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT horario_cita
        CHECK (
            hora IN (
                '09:00', '10:00', '11:00', '12:00', '01:00'
                '04:00', '05:00', '06:00', '07:00'
            )
        ),

    CONSTRAINT medico_horario_unico UNIQUE (id_medico, fecha, hora),
    CONSTRAINT paciente_horario_unico UNIQUE (id_paciente, fecha, hora)
);