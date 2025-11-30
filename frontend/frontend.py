import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime
import time

# Конфигурация API и приложения
API_BASE_URL = "http://backend:8090"
st.set_page_config(page_title="TaskTracker", layout="wide")

# Инициализация session state
if 'request_cache' not in st.session_state:
    st.session_state.request_cache = {}
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = {}
if 'form_submissions' not in st.session_state:
    st.session_state.form_submissions = {}


def validate_phone(phone):
    """Валидация российского номера телефона"""
    if not phone:
        return True
    pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    return re.match(pattern, phone) is not None


def validate_email(email):
    """Валидация email"""
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def make_request(endpoint, method="GET", data=None, force=False):
    """Универсальная функция для API запросов с защитой от дублирования"""
    # Создаем уникальный ключ для запроса
    request_key = f"{method}_{endpoint}_{str(data)}"

    # Проверяем кэш и временную метку
    current_time = time.time()
    if (not force and
            request_key in st.session_state.request_cache and
            request_key in st.session_state.last_request_time and
            current_time - st.session_state.last_request_time[request_key] < 2.0):  # 2 секунды кэш
        return st.session_state.request_cache[request_key]

    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = None
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
        else:
            st.error(f"Неизвестный метод: {method}")
            return None

        if response.status_code in [200, 201, 204]:
            result = response.json() if response.content else True
            # Кэшируем результат
            st.session_state.request_cache[request_key] = result
            st.session_state.last_request_time[request_key] = current_time
            return result
        else:
            st.error(f"Ошибка: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("Не удалось подключиться к серверу. Убедитесь, что бэкенд запущен на порту 8090.")
        return None
    except requests.exceptions.Timeout:
        st.error("Таймаут подключения к серверу.")
        return None
    except Exception as e:
        st.error(f"Ошибка подключения: {e}")
        return None


def is_form_submitted(form_key):
    """Проверяет, была ли форма уже отправлена в текущем запуске"""
    return st.session_state.form_submissions.get(form_key, False)


def mark_form_submitted(form_key):
    """Отмечает форму как отправленную"""
    st.session_state.form_submissions[form_key] = True


def clear_form_submissions():
    """Очищает все отправленные формы (вызывать после успешного действия)"""
    st.session_state.form_submissions.clear()


def safe_form_submit(form_key, action_function, *args, **kwargs):
    """Безопасная отправка формы с защитой от дублирования"""
    if is_form_submitted(form_key):
        st.warning("Запрос уже обрабатывается...")
        return None

    mark_form_submitted(form_key)
    result = action_function(*args, **kwargs)

    # Если действие успешно, очищаем кэш запросов
    if result:
        clear_form_submissions()
        # Очищаем ВЕСЬ кэш запросов чтобы обновить данные
        st.session_state.request_cache.clear()
        st.session_state.last_request_time.clear()

    return result


def show_backlog_page():
    """Главная страница - бэклог всех задач"""
    st.header("📋 Бэклог задач")

    # Получаем все данные с принудительным обновлением
    tasks = make_request("/tasks/", force=True)
    employees = make_request("/employees/", force=True)
    projects = make_request("/projects/", force=True)

    if not tasks:
        st.info("Задачи не найдены. Создайте первую задачу!")
        return

    # Обогащаем задачи данными о проектах и сотрудниках
    enriched_tasks = []
    for task in tasks:
        project = next((p for p in projects if p['id'] == task['project_id']), {}) if projects else {}
        employee = next((e for e in employees if e['id'] == task['employee_id']), {}) if task.get(
            'employee_id') and employees else None

        enriched_task = {
            'id': task['id'],
            'name': task['name'],
            'description': task.get('description', ''),
            'needed_hours': task.get('needed_hours', 0),
            'status': task.get('status', 'Новая'),
            'priority': task.get('priority', 'Средний'),
            'employee_name': f"{employee.get('name', '')} {employee.get('surname', '')}".strip() if employee else 'Не назначен',
            'project_name': project.get('name', 'Неизвестно'),
        }
        enriched_tasks.append(enriched_task)

    # Создаем DataFrame для отображения
    display_df = pd.DataFrame(enriched_tasks)
    display_df = display_df[
        ['id', 'name', 'description', 'needed_hours', 'status', 'priority', 'employee_name', 'project_name']]
    display_df.columns = ['ID', 'Название', 'Описание', 'Часы', 'Статус', 'Приоритет', 'Исполнитель', 'Проект']

    # Заменяем None значения
    display_df['Описание'] = display_df['Описание'].fillna('Нет описания')
    display_df['Исполнитель'] = display_df['Исполнитель'].fillna('Не назначен')

    # Красивое отображение статусов и приоритетов
    status_icons = {'Новая': '⏳ Новая', 'В работе': '🔄 В работе', 'Выполнена': '✅ Выполнена'}
    priority_icons = {'Низкий': '🟢 Низкий', 'Средний': '🟡 Средний', 'Высокий': '🔴 Высокий'}

    display_df['Статус'] = display_df['Статус'].map(status_icons).fillna(display_df['Статус'])
    display_df['Приоритет'] = display_df['Приоритет'].map(priority_icons).fillna(display_df['Приоритет'])

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox("Статус", ["Все", "Новая", "В работе", "Выполнена"], key="status_filter")
    with col2:
        priority_filter = st.selectbox("Приоритет", ["Все", "Низкий", "Средний", "Высокий"], key="priority_filter")
    with col3:
        employee_options = ["Все"]
        if employees:
            employee_options.extend([f"{e['id']} - {e['name']} {e['surname']}" for e in employees])
        employee_filter = st.selectbox("Исполнитель", employee_options, key="employee_filter")

    # Применяем фильтры
    filtered_df = display_df.copy()

    if status_filter != "Все":
        status_map = {v: k for k, v in status_icons.items()}
        filtered_df['status_clean'] = filtered_df['Статус'].map(status_map).fillna(filtered_df['Статус'])
        filtered_df = filtered_df[filtered_df['status_clean'] == status_filter]

    if priority_filter != "Все":
        priority_map = {v: k for k, v in priority_icons.items()}
        filtered_df['priority_clean'] = filtered_df['Приоритет'].map(priority_map).fillna(filtered_df['Приоритет'])
        filtered_df = filtered_df[filtered_df['priority_clean'] == priority_filter]

    if employee_filter != "Все":
        employee_name = employee_filter.split(" - ")[1] if " - " in employee_filter else employee_filter
        filtered_df = filtered_df[filtered_df['Исполнитель'] == employee_name]

    # Удаляем временные колонки
    filtered_df = filtered_df.drop(columns=['status_clean', 'priority_clean'], errors='ignore')

    # Отображаем отфильтрованную таблицу
    st.dataframe(filtered_df, use_container_width=True)


def show_users_page():
    """Страница управления пользователями и ролями"""
    st.header("👥 Сотрудники")

    # Добавление сотрудника
    with st.expander("➕ Добавить сотрудника", expanded=False):
        with st.form(key="add_employee_form", clear_on_submit=True):
            name = st.text_input("Имя*")
            surname = st.text_input("Фамилия*")
            patronymic = st.text_input("Отчество")
            phone_number = st.text_input("Телефон*", placeholder="+7 XXX XXX-XX-XX")
            mail = st.text_input("Email*", placeholder="example@mail.ru")
            role = st.selectbox("Роль*", ["Менеджер", "Разработчик", "Тестировщик", "Аналитик"])

            if st.form_submit_button("Добавить сотрудника"):
                def add_employee():
                    if not name.strip() or not surname.strip():
                        st.info("Имя и фамилия обязательны для заполнения!")
                        return False
                    if not mail.strip() and not phone_number.strip():
                        st.info("Почта и номер телефона обязательны для заполнения!")
                        return False
                    if not mail.strip():
                        st.info("Почта обязательна для заполнения!")
                        return False
                    if not phone_number.strip():
                        st.info("Номер телефона обязателен для заполнения!")
                        return False
                    if phone_number and not validate_phone(phone_number):
                        st.info("Неверный формат телефона! Используйте российский формат.")
                        return False
                    if mail and not validate_email(mail):
                        st.info("Неверный формат email!")
                        return False

                    employee_data = {
                        "name": name.strip(),
                        "surname": surname.strip(),
                        "patronymic": patronymic.strip() if patronymic else None,
                        "phone_number": phone_number.strip(),
                        "mail": mail.strip(),
                        "role": role
                    }
                    result = make_request("/employees/", "POST", employee_data)
                    if result:
                        st.success("Сотрудник успешно добавлен!")
                        return True
                    return False

                safe_form_submit(f"add_employee_{name}_{surname}", add_employee)

    # Список сотрудников
    st.subheader("📋 Список пользователей")
    employees = make_request("/employees/", force=True)

    if employees:
        employees_df = pd.DataFrame(employees)
        st.dataframe(employees_df, use_container_width=True)

        # Редактирование и удаление сотрудников
        st.subheader("⚙️ Управление сотрудниками")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**✏️ Редактировать сотрудника**")
            employee_options = [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]
            selected_employee = st.selectbox("Выберите сотрудника", employee_options, key="edit_employee_select")

            if selected_employee:
                employee_id = int(selected_employee.split(" - ")[0])
                employee = next((e for e in employees if e["id"] == employee_id), None)

                if st.session_state.get('employee_updated', False):
                    st.success("Данные сотрудника обновлены!")
                    st.session_state.employee_updated = False

                if employee:
                    with st.form(key=f"edit_employee_form_{employee_id}"):
                        new_name = st.text_input("Имя*", value=employee["name"])
                        new_surname = st.text_input("Фамилия*", value=employee["surname"])
                        new_patronymic = st.text_input("Отчество", value=employee["patronymic"] or "")
                        new_phone = st.text_input("Телефон", value=employee["phone_number"] or "",
                                                  placeholder="+7 XXX XXX-XX-XX")
                        new_mail = st.text_input("Email", value=employee["mail"] or "", placeholder="example@mail.ru")
                        new_role = st.selectbox("Роль", ["Менеджер", "Разработчик", "Тестировщик", "Аналитик"],
                                                index=["Менеджер", "Разработчик", "Тестировщик", "Аналитик"].index(
                                                    employee.get("role", "Разработчик")))

                        if st.form_submit_button("Обновить сотрудника"):
                            if not new_name or not new_surname:
                                st.error("Имя и фамилия обязательны для заполнения!")
                                return False
                            if new_phone and not validate_phone(new_phone):
                                st.error("Неверный формат телефона!")
                                return False
                            if new_mail and not validate_email(new_mail):
                                st.error("Неверный формат email!")
                                return False

                            update_data = {
                                "name": new_name,
                                "surname": new_surname,
                                "patronymic": new_patronymic,
                                "phone_number": new_phone,
                                "mail": new_mail,
                                "role": new_role
                            }
                            result = make_request(f"/employees/{employee_id}", "PUT", update_data)
                            if result:
                                st.session_state.employee_updated = True
                                st.rerun()
                            else:
                                st.error("Ошибка при обновлении сотрудника!")

        with col2:
            st.write("**🗑️ Удалить сотрудника**")
            delete_employee = st.selectbox("Выберите сотрудника для удаления", employee_options,
                                           key="delete_employee_select")

            if st.session_state.get('employee_deleted', False):
                st.success("Данные сотрудника удалены!")
                st.session_state.employee_deleted = False

            if st.button("Удалить сотрудника", key=f"delete_employee_btn"):
                employee_id = int(delete_employee.split(" - ")[0])
                result = make_request(f"/employees/{employee_id}", "DELETE")
                if result:
                    st.session_state.employee_deleted = True
                    st.rerun()
                else:
                    st.error("Ошибка при удалении сотрудника!")
            return None
    else:
        st.info("Сотрудники не найдены. Добавьте первого сотрудника!")
        return None

def show_projects_page():
    """Страница управления проектами"""
    st.header("🗂️ Управление проектами")

    # Создание проекта
    with st.expander("➕ Создать новый проект"):
        with st.form(key="create_project_form", clear_on_submit=True):
            name = st.text_input("Название проекта*")
            description = st.text_area("Описание")
            start_date = st.date_input("Дата начала")
            finish_date = st.date_input("Дата окончания")

            if st.form_submit_button("Создать проект"):
                def create_project():
                    if not name:
                        st.error("Название проекта обязательно!")
                        return False
                    if finish_date and start_date and finish_date < start_date:
                        st.error("Дата окончания не может быть раньше даты начала!")
                        return False

                    project_data = {
                        "name": name,
                        "description": description,
                        "start_date": start_date.isoformat() if start_date else None,
                        "finish_date": finish_date.isoformat() if finish_date else None
                    }
                    result = make_request("/projects/", "POST", project_data)
                    if result:
                        st.success("Проект успешно создан!")
                        return True
                    return False

                safe_form_submit(f"create_project_{name}", create_project)

    # Список проектов
    st.subheader("📊 Список проектов")
    projects = make_request("/projects/", force=True)

    if projects:
        projects_df = pd.DataFrame(projects)
        st.dataframe(projects_df, use_container_width=True)

        # Редактирование и удаление проектов
        st.subheader("⚙️ Настройка проектов")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**✏️ Редактировать проект**")
            project_names = [p["name"] for p in projects]
            selected_project = st.selectbox("Выберите проект", project_names, key="edit_project_select")

            if selected_project:
                project = next((p for p in projects if p["name"] == selected_project), None)
                if project:
                    # Проверяем, не нужно ли сделать rerun после обновления
                    if st.session_state.get('project_updated', False):
                        st.success("Проект обновлен!")
                        st.session_state.project_updated = False

                    with st.form(key=f"edit_project_form_{project['id']}"):
                        new_name = st.text_input("Название*", value=project["name"])
                        new_description = st.text_area("Описание", value=project["description"] or "")

                        start_date_current = datetime.fromisoformat(project["start_date"]) if project[
                            "start_date"] else None
                        finish_date_current = datetime.fromisoformat(project["finish_date"]) if project[
                            "finish_date"] else None

                        new_start_date = st.date_input("Дата начала", value=start_date_current)
                        new_finish_date = st.date_input("Дата окончания", value=finish_date_current)

                        submitted = st.form_submit_button("Обновить проект")

                        if submitted:
                            if not new_name:
                                st.error("Название проекта обязательно!")
                            elif new_finish_date and new_start_date and new_finish_date < new_start_date:
                                st.error("Дата окончания не может быть раньше даты начала!")
                            else:
                                update_data = {
                                    "name": new_name,
                                    "description": new_description,
                                    "start_date": new_start_date.isoformat() if new_start_date else None,
                                    "finish_date": new_finish_date.isoformat() if new_finish_date else None
                                }
                                result = make_request(f"/projects/{selected_project}", "PUT", update_data)

                                if result:
                                    st.session_state.project_updated = True
                                    st.rerun()
                                else:
                                    st.error("Ошибка при обновлении проекта!")

        with col2:
            st.write("**🗑️ Удалить проект**")
            delete_project = st.selectbox("Выберите проект для удаления", project_names, key="delete_project_select")
            if st.session_state.get('project_deleted', False):
                st.success("Проект удален!")
                st.session_state.project_deleted = False

            if st.button("Удалить проект", key=f"delete_project_btn"):
                result = make_request(f"/projects/{delete_project}", "DELETE")
                if result:
                    st.session_state.project_deleted = True
                    st.rerun()
                else:
                    st.error("Ошибка при обновлении проекта!")
            return None
    else:
        st.info("Проекты не найдены. Создайте первый проект!")
        return None


def show_assignments_page():
    """Страница назначений сотрудников на проекты"""
    st.header("🔗 Назначения сотрудников на проекты")

    employees = make_request("/employees/", force=True)
    projects = make_request("/projects/", force=True)

    if not employees or not projects:
        if not employees:
            st.info("Нельзя назначить сотрудника на проект при отсутствии сотрудников.")
        if not projects:
            st.info("Нельзя назначить сотрудника на проект при отсутствии проектов.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Добавить сотрудника в проект")
        with st.form(key="add_assignment_form", clear_on_submit=True):
            employee_options = [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]
            project_options = [f"{p['id']} - {p['name']}" for p in projects]

            selected_employee = st.selectbox("Сотрудник", employee_options)
            selected_project = st.selectbox("Проект", project_options)

            if st.form_submit_button("Добавить в проект"):
                def add_assignment():
                    # Извлекаем ID из выбранных значений
                    employee_id = int(selected_employee.split(" - ")[0])
                    project_id = int(selected_project.split(" - ")[0])

                    assignment_data = {
                        "employee_id": employee_id,
                        "project_id": project_id
                    }
                    result = make_request("/employee-projects/", "POST", assignment_data)
                    if result:
                        st.success("Сотрудник успешно добавлен в проект!")
                        return True
                    return False

                # Создаем уникальный ключ для формы
                form_key = f"add_assignment_{selected_employee}_{selected_project}"
                safe_form_submit(form_key, add_assignment)

    with col2:
        st.subheader("🗑️ Удалить сотрудника из проекта")
        assignments = make_request("/employee-projects/", force=True)

        if assignments:
            with st.form(key="remove_assignment_form", clear_on_submit=True):
                employee_options = [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]
                project_options = [f"{p['id']} - {p['name']}" for p in projects]

                selected_employee = st.selectbox("Сотрудник", employee_options)
                selected_project = st.selectbox("Проект", project_options)

                if st.form_submit_button("Удалить из проекта"):
                    def remove_assignment():
                        # Извлекаем ID из выбранного назначения
                        employee_id = int(selected_employee.split(" - ")[0])
                        project_id = int(selected_project.split(" - ")[0])

                        if make_request(f"/employee-projects/?employee_id={employee_id}&project_id={project_id}",
                                        "DELETE"):
                            st.success("Сотрудник удален из проекта!")
                            return True
                        return False

                    # Создаем уникальный ключ для формы
                    form_key = f"remove_assignment_{selected_employee}_{selected_project}"
                    safe_form_submit(form_key, remove_assignment)
        else:
            st.info("Нет активных назначений")

    # Просмотр назначений
    st.subheader("👀 Текущие назначения")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**📋 Проекты и их сотрудники**")
        selected_project_view = st.selectbox("Выберите проект", [f"{p['id']} - {p['name']}" for p in projects],
                                             key="project_view")

        if selected_project_view:
            project_id = int(selected_project_view.split(" - ")[0])
            project_employees = make_request(f"/employee-projects/projects/{project_id}/employees", force=True)
            if project_employees and project_employees.get("employees"):
                employees_df = pd.DataFrame(project_employees["employees"])
                st.dataframe(employees_df, use_container_width=True)
            else:
                st.info("В этом проекте нет сотрудников")

    with col2:
        st.write("**👥 Сотрудники и их проекты**")
        selected_employee_view = st.selectbox("Выберите сотрудника",
                                              [f"{e['id']} - {e['name']} {e['surname']}" for e in employees],
                                              key="employee_view")

        if selected_employee_view:
            employee_id = int(selected_employee_view.split(" - ")[0])
            employee_projects = make_request(f"/employee-projects/employees/{employee_id}/projects", force=True)
            if employee_projects and employee_projects.get("projects"):
                projects_df = pd.DataFrame(employee_projects["projects"])
                st.dataframe(projects_df, use_container_width=True)
            else:
                st.info("У этого сотрудника нет проектов")


def show_tasks_page():
    """Страница управления задачами"""
    st.header("✅ Управление задачами")

    projects = make_request("/projects/", force=True)
    employees = make_request("/employees/", force=True)
    tasks = make_request("/tasks/", force=True)

    if not projects:
        st.info("Нельзя создавать задачи без проектов. Сначала создайте проект во вкладке 'Проекты'.")
        return

    # Создание задачи
    with st.expander("➕ Создать новую задачу"):
        if projects and employees:
            with st.form(key="create_task_form", clear_on_submit=True):
                project_options = [f"{p['id']} - {p['name']}" for p in projects]
                employee_options = ["Не назначено"] + [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]

                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Название задачи*")
                    selected_project = st.selectbox("Проект*", project_options)
                    needed_hours = st.number_input("Необходимо часов", min_value=0, value=0)
                    priority = st.selectbox("Приоритет", ["Низкий", "Средний", "Высокий"])

                with col2:
                    description = st.text_area("Описание")
                    selected_employee = st.selectbox("Исполнитель", employee_options)
                    status = st.selectbox("Статус", ["Новая", "В работе", "Выполнена"])

                if st.form_submit_button("Создать задачу"):
                    def create_task():
                        if not name:
                            st.error("Название задачи обязательно!")
                            return False

                        project_id = int(selected_project.split(" - ")[0])
                        task_data = {
                            "name": name,
                            "description": description,
                            "needed_hours": needed_hours,
                            "status": status,
                            "priority": priority,
                            "project_id": project_id,
                            "employee_id": int(
                                selected_employee.split(" - ")[0]) if selected_employee != "Не назначено" else None
                        }
                        result = make_request("/tasks/", "POST", task_data)
                        if result:
                            st.success("Задача успешно создана!")
                            # Принудительно обновляем данные
                            st.session_state.request_cache.clear()
                            return True
                        return False

                    safe_form_submit(f"create_task_{name}", create_task)
        else:
            st.error("Не удалось загрузить данные проектов и сотрудников")

    # Список задач
    st.subheader("📋 Список задач")

    if tasks:
        # Обогащаем задачи данными
        enriched_tasks = []
        for task in tasks:
            project = next((p for p in projects if p['id'] == task['project_id']), {})
            employee = next((e for e in employees if e['id'] == task['employee_id']), {}) if task.get(
                'employee_id') else None

            enriched_task = {
                'id': task['id'],
                'name': task['name'],
                'description': task.get('description', ''),
                'needed_hours': task.get('needed_hours', 0),
                'status': task.get('status', 'Новая'),
                'priority': task.get('priority', 'Средний'),
                'employee_name': f"{employee.get('name', '')} {employee.get('surname', '')}".strip() if employee else 'Не назначен',
                'project_name': project.get('name', 'Неизвестно'),
            }
            enriched_tasks.append(enriched_task)

        # Отображаем задачи
        display_df = pd.DataFrame(enriched_tasks)
        display_df = display_df[
            ['id', 'name', 'description', 'needed_hours', 'status', 'priority', 'employee_name', 'project_name']]
        display_df.columns = ['ID', 'Название', 'Описание', 'Часы', 'Статус', 'Приоритет', 'Исполнитель', 'Проект']

        display_df['Описание'] = display_df['Описание'].fillna('Нет описания')
        display_df['Исполнитель'] = display_df['Исполнитель'].fillna('Не назначен')

        st.dataframe(display_df, use_container_width=True)

        task_options = [f"{t['id']} - {t['name']}" for t in enriched_tasks]

        # Редактирование задачи
        st.write("---")
        st.write("**✏️ Редактировать задачу**")
        selected_task_edit = st.selectbox("Выберите задачу", task_options, key="edit_task_select")

        if selected_task_edit:
            task_id = int(selected_task_edit.split(" - ")[0])
            task = next((t for t in enriched_tasks if t['id'] == task_id), None)

            if st.session_state.get('task_updated', False):
                st.success("Данные задачи обновлены!")
                st.session_state.task_updated = False

            employees = make_request("/employees/", force=True)
            employee_options = [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]

            if task:
                with st.form(key=f"edit_task_form_{task_id}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_name = st.text_input("Название*", value=task["name"])
                        new_description = st.text_area("Описание", value=task["description"] or "")
                        new_hours = st.number_input("Необходимо часов", value=task["needed_hours"] or 0, min_value=0)
                        new_priority = st.selectbox("Новый приоритет", ["Низкий", "Средний", "Высокий"],
                                                    key="new_priority_select")
                        new_status = st.selectbox("Новый статус", ["Новая", "В работе", "Выполнена"],
                                                    key="new_status_select")
                        selected_employee = st.selectbox("Сотрудник", employee_options)
                        employee_id = int(selected_employee.split(" - ")[0])

                    if st.form_submit_button("Обновить задачу"):
                        if not new_name:
                            st.error("Название задачи обязательно!")
                        else:
                            update_data = {
                                "name": new_name,
                                "description": new_description,
                                "needed_hours": new_hours,
                                "priority": new_priority,
                                "status": new_status,
                                "employee_id": employee_id
                            }
                            result = make_request(f"/tasks/{task_id}", "PUT", update_data)

                            if result:
                                st.session_state.task_updated = True
                                st.rerun()
                            else:
                                st.error("Ошибка при обновлении задачи!")

        # Удаление задачи
        st.write("---")
        st.write("**🗑️ Удаление задачи**")
        delete_task = st.selectbox("Выберите задачу для удаления", task_options, key="delete_task_select")

        if st.session_state.get('task_deleted', False):
            st.success("Задача удалена!")
            st.session_state.task_deleted = False

        if st.button("Удалить задачу", key="delete_task_btn"):
            task_id = int(delete_task.split(" - ")[0])
            result = make_request(f"/tasks/{task_id}", "DELETE")
            if result:
                st.session_state.task_deleted = True
                st.rerun()
            else:
                st.error("Ошибка при удалении задачи!")
    else:
        st.info("Задачи не найдены. Создайте первую задачу!")

    # Фильтрация задач
    st.subheader("🔍 Фильтры задач")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**📋 Задачи по проекту**")
        if projects:
            selected_project_filter = st.selectbox("Выберите проект", [f"{p['id']} - {p['name']}" for p in projects],
                                                   key="project_filter")

            if selected_project_filter:
                project_id = int(selected_project_filter.split(" - ")[0])
                project_tasks = make_request(f"/tasks/project/{project_id}", force=True)

                if project_tasks:
                    st.write(f"Задачи проекта ({len(project_tasks)}):")
                    for task in project_tasks:
                        status_icon = "⏳" if task["status"] == "Новая" else "🔄" if task["status"] == "В работе" else "✅"
                        st.write(f"- {status_icon} {task['name']} (Часы: {task['needed_hours'] or 'не указано'})")
                else:
                    st.info("В этом проекте нет задач")

    with col2:
        st.write("**👤 Задачи по исполнителю**")
        if employees:
            selected_employee_filter = st.selectbox("Выберите исполнителя",
                                                    [f"{e['id']} - {e['name']} {e['surname']}" for e in employees],
                                                    key="employee_filter")

            if selected_employee_filter:
                employee_id = int(selected_employee_filter.split(" - ")[0])
                employee_tasks = make_request(f"/tasks/employee/{employee_id}", force=True)

                if employee_tasks:
                    st.write(f"Задачи сотрудника ({len(employee_tasks)}):")
                    for task in employee_tasks:
                        status_icon = "⏳" if task["status"] == "Новая" else "🔄" if task["status"] == "В работе" else "✅"
                        st.write(f"- {status_icon} {task['name']} (Статус: {task['status']})")
                else:
                    st.info("У этого сотрудника нет задач")


def main():
    """Главная функция приложения"""
    st.title("Платформа для управления задачами")

    # Боковая панель навигации
    st.sidebar.title("Навигация")
    page = st.sidebar.radio("Выберите раздел:", [
        "🗂️ Проекты",
        "👥 Сотрудники",
        "✅ Задачи",
        "🔗 Назначения",
        "📋 Бэклог задач",
    ])

    # Маршрутизация по страницам
    if page == "📋 Бэклог задач":
        show_backlog_page()
    elif page == "👥 Сотрудники":
        show_users_page()
    elif page == "🗂️ Проекты":
        show_projects_page()
    elif page == "🔗 Назначения":
        show_assignments_page()
    elif page == "✅ Задачи":
        show_tasks_page()


if __name__ == "__main__":
    main()