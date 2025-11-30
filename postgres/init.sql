CREATE TYPE role_type AS ENUM ('Менеджер', 'Разработчик', 'Тестировщик', 'Аналитик');
CREATE TYPE status_type AS ENUM ('Новая', 'В работе', 'Выполнена');
CREATE TYPE priority_enum AS ENUM ('Низкий', 'Средний', 'Высокий');

CREATE TABLE IF NOT EXISTS employee (
    id SERIAL PRIMARY KEY,
    name text NOT NULL,
    surname text NOT NULL,
    patronymic text,
    phone_number text NOT NULL,
    mail text NOT NULL,
    role role_type DEFAULT 'Разработчик'
);

CREATE TABLE IF NOT EXISTS project (
    id SERIAL PRIMARY KEY,
    name text NOT NULL UNIQUE,
    description text,
    start_date timestamp with time zone,
    finish_date timestamp with time zone
);

CREATE TABLE IF NOT EXISTS employee_project (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    project_id INTEGER
);

CREATE TABLE IF NOT EXISTS task (
    id SERIAL PRIMARY KEY,
    name text NOT NULL,
    description text,
    needed_hours INTEGER,
    status status_type DEFAULT 'Новая',
    priority priority_enum DEFAULT 'Средний',
    project_id INTEGER NOT NULL,
    employee_id INTEGER
);