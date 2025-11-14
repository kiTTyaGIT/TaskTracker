import streamlit as st
import requests
import pandas as pd
import re
from datetime import datetime

# Конфигурация API и приложения
API_BASE_URL = "http://localhost:8090"
st.set_page_config(page_title="TaskTracker", layout="wide")


def validate_phone(phone):
    """Валидация российского номера телефона"""
    pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    return re.match(pattern, phone) is not None


def validate_email(email):
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def make_request(endpoint, method="GET", data=None):
    """Универсальная функция для API запросов"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        elif method == "PATCH":
            response = requests.patch(url, json=data)
        else:
            st.error(f"Неизвестный метод: {method}")
            return None

        if response.status_code in [200, 201, 204]:
            return response.json() if response.content else True
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


def show_backlog_page():
    """Главная страница - бэклог всех задач"""
    st.header("📋 Бэклог задач")

    # Получаем все данные
    tasks = make_request("/tasks/")
    employees = make_request("/employees/")
    projects = make_request("/projects/")

    if not tasks:
        st.info("Задачи не найдены. Создайте первую задачу!")
        return

    # Обогащаем задачи данными о проектах и сотрудниках
    enriched_tasks = []
    for task in tasks:
        # Находим проект
        project = next((p for p in projects if p['id'] == task['project_id']), {}) if projects else {}
        # Находим сотрудника
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
            'project_id': task['project_id'],
            'employee_id': task.get('employee_id')
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

    # Красивое отображение статусов
    status_icons = {
        'Новая': '⏳ Новая',
        'В работе': '🔄 В работе',
        'Выполнена': '✅ Выполнена'
    }
    display_df['Статус'] = display_df['Статус'].map(status_icons).fillna(display_df['Статус'])

    # Красивое отображение приоритетов
    priority_icons = {
        'Низкий': '🟢 Низкий',
        'Средний': '🟡 Средний',
        'Высокий': '🔴 Высокий'
    }
    display_df['Приоритет'] = display_df['Приоритет'].map(priority_icons).fillna(display_df['Приоритет'])

    # Фильтрация данных
    st.subheader("🔍 Фильтры задач")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Фильтр по статусу
        status_filter = st.selectbox(
            "Статус",
            ["Все", "Новая", "В работе", "Выполнена"],
            key="status_filter"
        )

    with col2:
        # Фильтр по приоритету
        priority_filter = st.selectbox(
            "Приоритет",
            ["Все", "Низкий", "Средний", "Высокий"],
            key="priority_filter"
        )

    with col3:
        # Фильтр по исполнителю
        employee_options = ["Все"]
        if employees:
            employee_options.extend([f"{e['id']} - {e['name']} {e['surname']}" for e in employees])

        employee_filter = st.selectbox("Исполнитель", employee_options, key="employee_filter")

    # Применяем фильтры
    filtered_df = display_df.copy()

    if status_filter != "Все":
        # Убираем иконки для фильтрации
        status_map = {v: k for k, v in status_icons.items()}
        filtered_df['status_clean'] = filtered_df['Статус'].map(status_map).fillna(filtered_df['Статус'])
        filtered_df = filtered_df[filtered_df['status_clean'] == status_filter]

    if priority_filter != "Все":
        # Убираем иконки для фильтрации
        priority_map = {v: k for k, v in priority_icons.items()}
        filtered_df['priority_clean'] = filtered_df['Приоритет'].map(priority_map).fillna(filtered_df['Приоритет'])
        filtered_df = filtered_df[filtered_df['priority_clean'] == priority_filter]

    if employee_filter != "Все":
        employee_name = employee_filter.split(" - ")[1] if " - " in employee_filter else employee_filter
        filtered_df = filtered_df[filtered_df['Исполнитель'] == employee_name]

    # Удаляем временные колонки
    if 'status_clean' in filtered_df.columns:
        filtered_df = filtered_df.drop('status_clean', axis=1)
    if 'priority_clean' in filtered_df.columns:
        filtered_df = filtered_df.drop('priority_clean', axis=1)

    # Отображаем отфильтрованную таблицу
    st.dataframe(filtered_df, use_container_width=True)

    # Статистика
    st.subheader("📊 Статистика задач")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_tasks = len(filtered_df)
        st.metric("Всего задач", total_tasks)

    with col2:
        # Считаем задачи "В работе" по чистым статусам
        in_progress_count = len([t for t in enriched_tasks if t['status'] == 'В работе' and
                                 (status_filter == "Все" or status_filter == "В работе") and
                                 (priority_filter == "Все" or priority_filter == t['priority']) and
                                 (employee_filter == "Все" or f"{t['employee_name']}" == employee_filter.split(" - ")[
                                     1] if " - " in employee_filter else employee_filter)])
        st.metric("В работе", in_progress_count)

    with col3:
        # Считаем выполненные задачи по чистым статусам
        completed_count = len([t for t in enriched_tasks if t['status'] == 'Выполнена' and
                               (status_filter == "Все" or status_filter == "Выполнена") and
                               (priority_filter == "Все" or priority_filter == t['priority']) and
                               (employee_filter == "Все" or f"{t['employee_name']}" == employee_filter.split(" - ")[
                                   1] if " - " in employee_filter else employee_filter)])
        st.metric("Выполнено", completed_count)

    with col4:
        # Считаем задачи высокого приоритета по чистым приоритетам
        high_priority_count = len([t for t in enriched_tasks if t['priority'] == 'Высокий' and
                                   (priority_filter == "Все" or priority_filter == "Высокий") and
                                   (status_filter == "Все" or status_filter == t['status']) and
                                   (employee_filter == "Все" or f"{t['employee_name']}" == employee_filter.split(" - ")[
                                       1] if " - " in employee_filter else employee_filter)])
        st.metric("Высокий приоритет", high_priority_count)


def show_users_page():
    """Страница управления пользователями и ролями"""
    st.header("👥 Сотрудники и роли")

    # Создание нового сотрудника
    with st.expander("➕ Добавить сотрудника"):
        with st.form("create_employee"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Имя*")
                surname = st.text_input("Фамилия*")
                patronymic = st.text_input("Отчество")
                role = st.selectbox("Роль*", ["Менеджер", "Разработчик", "Тестировщик", "Аналитик"])

            with col2:
                phone_number = st.text_input("Телефон", placeholder="+7 XXX XXX-XX-XX")
                mail = st.text_input("Email*", placeholder="example@mail.ru")

            if st.form_submit_button("Добавить сотрудника"):
                # Валидация обязательных полей
                if not name.replace(" ", "") or not surname.replace(" ", "") or not mail:
                    st.error("Имя, фамилия и email обязательны для заполнения!")
                # Валидация телефона, если указан
                elif phone_number and not validate_phone(phone_number):
                    st.error("Неверный формат телефона! Используйте российский формат.")
                # Валидация email
                elif not validate_email(mail):
                    st.error("Неверный формат email!")
                else:
                    employee_data = {
                        "name": name,
                        "surname": surname,
                        "patronymic": patronymic,
                        "phone_number": phone_number,
                        "mail": mail,
                        "role": role
                    }
                    result = make_request("/employees/", "POST", employee_data)
                    if result:
                        st.success("Сотрудник успешно добавлен!")
                        st.rerun()

    # Список сотрудников с ролями
    st.subheader("📋 Список пользователей")
    employees = make_request("/employees/")

    if employees:
        employees_df = pd.DataFrame(employees)
        st.dataframe(employees_df, use_container_width=True)

        # Редактирование и удаление сотрудников
        st.subheader("⚙️ Управление сотрудниками")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**✏️ Редактировать сотрудника**")
            employee_ids = [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]
            selected_employee = st.selectbox("Выберите сотрудника", employee_ids, key="edit_employee")

            if selected_employee:
                employee_id = int(selected_employee.split(" - ")[0])
                employee = next((e for e in employees if e["id"] == employee_id), None)
                if employee:
                    with st.form("edit_employee_form"):
                        new_name = st.text_input("Имя*", value=employee["name"])
                        new_surname = st.text_input("Фамилия*", value=employee["surname"])
                        new_patronymic = st.text_input("Отчество", value=employee["patronymic"] or "")
                        new_phone = st.text_input("Телефон", value=employee["phone_number"] or "",
                                                  placeholder="+7 XXX XXX-XX-XX")
                        new_mail = st.text_input("Email", value=employee["mail"] or "",
                                                 placeholder="example@mail.ru")

                        new_role = st.selectbox("Новая роль",
                                                ["Менеджер", "Разработчик", "Тестировщик", "Аналитик"],
                                                index=["Менеджер", "Разработчик", "Тестировщик", "Аналитик"].index(
                                                    employee.get("role", "Разработчик")))

                        if st.form_submit_button("Обновить сотрудника"):
                            if not new_name or not new_surname:
                                st.error("Имя и фамилия обязательны для заполнения!")
                            elif new_phone and not validate_phone(new_phone):
                                st.error("Неверный формат телефона! Используйте российский формат.")
                            elif new_mail and not validate_email(new_mail):
                                st.error("Неверный формат email!")
                            else:
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
                                    st.success("Данные сотрудника обновлены!")
                                    st.rerun()

        with col2:
            st.write("**🗑️ Удалить сотрудника**")
            delete_employee = st.selectbox("Выберите сотрудника для удаления", employee_ids, key="delete_employee")
            if st.button("Удалить сотрудника", type="secondary"):
                employee_id = int(delete_employee.split(" - ")[0])
                if make_request(f"/employees/{employee_id}", "DELETE"):
                    st.success("Сотрудник удален!")
                    st.rerun()
    else:
        st.info("Сотрудники не найдены. Добавьте первого сотрудника!")


def show_projects_page():
    """Страница управления проектами"""
    st.header("🗂️ Управление проектами")

    # Секция создания нового проекта
    with st.expander("➕ Создать новый проект"):
        with st.form("create_project"):
            name = st.text_input("Название проекта*")
            description = st.text_area("Описание")
            start_date = st.date_input("Дата начала")
            finish_date = st.date_input("Дата окончания")

            if st.form_submit_button("Создать проект"):
                if not name:
                    st.error("Название проекта обязательно!")
                elif finish_date and start_date and finish_date < start_date:
                    st.error("Дата окончания не может быть раньше даты начала!")
                else:
                    project_data = {
                        "name": name,
                        "description": description,
                        "start_date": start_date.isoformat() if start_date else None,
                        "finish_date": finish_date.isoformat() if finish_date else None
                    }
                    result = make_request("/projects/", "POST", project_data)
                    if result:
                        st.success("Проект успешно создан!")
                        st.rerun()

    # Отображение списка проектов
    st.subheader("📊 Список проектов")
    projects = make_request("/projects/")

    if projects:
        # Преобразуем в DataFrame для красивого отображения
        projects_df = pd.DataFrame(projects)
        st.dataframe(projects_df, use_container_width=True)

        # Редактирование и удаление проектов
        st.subheader("⚙️ Настройка проектов")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**✏️ Редактировать проект**")
            project_names = [p["name"] for p in projects]
            selected_project = st.selectbox("Выберите проект", project_names, key="edit_project")

            if selected_project:
                project = next((p for p in projects if p["name"] == selected_project), None)
                if project:
                    with st.form("edit_project_form"):
                        new_name = st.text_input("Название*", value=project["name"])
                        new_description = st.text_area("Описание", value=project["description"] or "")

                        # Преобразуем строки дат в объекты datetime для отображения в date_input
                        start_date_current = datetime.fromisoformat(project["start_date"]) if project[
                            "start_date"] else None
                        finish_date_current = datetime.fromisoformat(project["finish_date"]) if project[
                            "finish_date"] else None

                        new_start_date = st.date_input("Дата начала", value=start_date_current)
                        new_finish_date = st.date_input("Дата окончания", value=finish_date_current)

                        if st.form_submit_button("Обновить проект"):
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
                                    st.success("Проект обновлен!")
                                    st.rerun()

        with col2:
            st.write("**🗑️ Удалить проект**")
            delete_project = st.selectbox("Выберите проект для удаления", project_names, key="delete_project")
            if st.button("Удалить проект", type="secondary"):
                if make_request(f"/projects/{delete_project}", "DELETE"):
                    st.success("Проект удален!")
                    st.rerun()
    else:
        st.info("Проекты не найдены. Создайте первый проект!")


def show_assignments_page():
    """Страница назначений сотрудников на проекты"""
    st.header("🔗 Назначения сотрудников на проекты")

    # Получаем данные
    employees = make_request("/employees/")
    projects = make_request("/projects/")

    if not employees or not projects:
        if not employees:
            st.info(
                "Нельзя назначить сотрудника на проект при отсутствии сотрудников. Добавьте сотрудника для назначения!")
        if not projects:
            st.info("Нельзя назначить сотрудника на проект при отсутствии проектов. Добавьте проект для назначения!")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Добавить сотрудника в проект")
        with st.form("add_assignment"):
            employee_options = [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]
            project_options = [f"{p['id']} - {p['name']}" for p in projects]

            selected_employee = st.selectbox("Сотрудник", employee_options)
            selected_project = st.selectbox("Проект", project_options)

            if st.form_submit_button("Добавить в проект"):
                employee_id = int(selected_employee.split(" - ")[0])
                project_id = int(selected_project.split(" - ")[0])

                assignment_data = {
                    "employee_id": employee_id,
                    "project_id": project_id
                }

                result = make_request("/employee-projects/", "POST", assignment_data)
                if result:
                    st.success("Сотрудник успешно добавлен в проект!")
                    st.rerun()

    with col2:
        st.subheader("🗑️ Удалить сотрудника из проекта")
        with st.form("remove_assignment"):
            # Получаем текущие назначения
            assignments = make_request("/employee-projects/")
            if assignments:
                assignment_options = [
                    f"Сотрудник {a['employee_id']} ⟶ Проект {a['project_id']}"
                    for a in assignments
                ]

                selected_assignment = st.selectbox("Выберите назначение", assignment_options)

                if st.form_submit_button("Удалить из проекта"):
                    employee_id = int(selected_assignment.split("Сотрудник ")[1].split(" ⟶")[0])
                    project_id = int(selected_assignment.split("Проект ")[1])

                    if make_request(f"/employee-projects/?employee_id={employee_id}&project_id={project_id}", "DELETE"):
                        st.success("Сотрудник удален из проекта!")
                        st.rerun()
            else:
                st.info("Нет активных назначений")

    # Просмотр назначений
    st.subheader("👀 Текущие назначения")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**📋 Проекты и их сотрудники**")
        selected_project_view = st.selectbox(
            "Выберите проект",
            [f"{p['id']} - {p['name']}" for p in projects],
            key="project_view"
        )

        if selected_project_view:
            project_id = int(selected_project_view.split(" - ")[0])
            project_employees = make_request(f"/employee-projects/projects/{project_id}/employees")
            if project_employees and project_employees.get("employees"):
                employees_df = pd.DataFrame(project_employees["employees"])
                st.dataframe(employees_df, use_container_width=True)
            else:
                st.info("В этом проекте нет сотрудников")

    with col2:
        st.write("**👥 Сотрудники и их проекты**")
        selected_employee_view = st.selectbox(
            "Выберите сотрудника",
            [f"{e['id']} - {e['name']} {e['surname']}" for e in employees],
            key="employee_view"
        )

        if selected_employee_view:
            employee_id = int(selected_employee_view.split(" - ")[0])
            employee_projects = make_request(f"/employee-projects/employees/{employee_id}/projects")
            if employee_projects and employee_projects.get("projects"):
                projects_df = pd.DataFrame(employee_projects["projects"])
                st.dataframe(projects_df, use_container_width=True)
            else:
                st.info("У этого сотрудника нет проектов")


def show_tasks_page():
    """Страница управления задачами"""
    st.header("✅ Управление задачами")

    # Получаем проекты и сотрудников для проверки
    projects = make_request("/projects/")
    employees = make_request("/employees/")
    tasks = make_request("/tasks/")

    # Проверяем, есть ли проекты для создания задач
    if not projects:
        st.info("Нельзя создавать задачи без проектов. Сначала создайте проект во вкладке 'Проекты'.")
        return

    # Создание новой задачи
    with st.expander("➕ Создать новую задачу"):
        with st.form("create_task"):
            if projects and employees:
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
                    if not name:
                        st.error("Название задачи обязательно!")
                    else:
                        # Правильно извлекаем ID проекта
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
                            st.rerun()
            else:
                st.error("Не удалось загрузить данные проектов и сотрудников")

    # Просмотр задач
    st.subheader("📋 Список задач")

    if tasks:
        # Обогащаем задачи данными о проектах и сотрудниках
        enriched_tasks = []
        for task in tasks:
            # Находим проект
            project = next((p for p in projects if p['id'] == task['project_id']), {})
            # Находим сотрудника
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
                'project_id': task['project_id'],
                'employee_id': task.get('employee_id')
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

        # Красивое отображение статусов
        status_icons = {
            'Новая': '⏳ Новая',
            'В работе': '🔄 В работе',
            'Выполнена': '✅ Выполнена'
        }
        display_df['Статус'] = display_df['Статус'].map(status_icons).fillna(display_df['Статус'])

        # Красивое отображение приоритетов
        priority_icons = {
            'Низкий': '🟢 Низкий',
            'Средний': '🟡 Средний',
            'Высокий': '🔴 Высокий'
        }
        display_df['Приоритет'] = display_df['Приоритет'].map(priority_icons).fillna(display_df['Приоритет'])

        st.dataframe(display_df, use_container_width=True)

        # Управление задачами
        st.subheader("⚙️ Управление задачами")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**👤 Назначить исполнителя**")
            task_options = [f"{t['id']} - {t['name']}" for t in enriched_tasks]
            selected_task_assign = st.selectbox("Выберите задачу", task_options, key="assign_task")

            if selected_task_assign:
                employee_options = ["Снять назначение"] + [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]
                selected_employee_assign = st.selectbox("Выберите исполнителя", employee_options, key="assign_employee")

                if st.button("Назначить"):
                    task_id = int(selected_task_assign.split(" - ")[0])
                    if selected_employee_assign == "Снять назначение":
                        # Снимаем назначение
                        update_data = {"employee_id": None}
                        result = make_request(f"/tasks/{task_id}", "PUT", update_data)
                    else:
                        employee_id = int(selected_employee_assign.split(" - ")[0])
                        result = make_request(f"/tasks/{task_id}/assign/{employee_id}", "PATCH")

                    if result:
                        st.success("Назначение обновлено!")
                        st.rerun()

        with col2:
            st.write("**🔄 Изменить статус**")
            selected_task_status = st.selectbox("Выберите задачу", task_options, key="status_task")

            if selected_task_status:
                new_status = st.selectbox("Новый статус", ["Новая", "В работе", "Выполнена"])

                if st.button("Обновить статус"):
                    task_id = int(selected_task_status.split(" - ")[0])
                    result = make_request(f"/tasks/{task_id}/status?status={new_status}", "PATCH")
                    if result:
                        st.success("Статус обновлен!")
                        st.rerun()

        with col3:
            st.write("**🎯 Изменить приоритет**")
            selected_task_priority = st.selectbox("Выберите задачу", task_options, key="priority_task")

            if selected_task_priority:
                new_priority = st.selectbox("Новый приоритет", ["Низкий", "Средний", "Высокий"])

                if st.button("Обновить приоритет"):
                    task_id = int(selected_task_priority.split(" - ")[0])
                    result = make_request(f"/tasks/{task_id}/priority?priority={new_priority}", "PATCH")
                    if result:
                        st.success("Приоритет обновлен!")
                        st.rerun()

        # Редактирование задачи
        st.write("---")
        st.write("**✏️ Редактировать задачу**")
        selected_task_edit = st.selectbox("Выберите задачу", task_options, key="edit_task")

        if selected_task_edit:
            task_id = int(selected_task_edit.split(" - ")[0])
            task = next((t for t in enriched_tasks if t['id'] == task_id), None)

            if task:
                with st.form("edit_task_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_name = st.text_input("Название", value=task["name"])
                        new_description = st.text_area("Описание", value=task["description"] or "")

                    with col2:
                        new_hours = st.number_input("Необходимо часов", value=task["needed_hours"] or 0, min_value=0)

                    if st.form_submit_button("Обновить задачу"):
                        update_data = {
                            "name": new_name,
                            "description": new_description,
                            "needed_hours": new_hours
                        }
                        result = make_request(f"/tasks/{task_id}", "PUT", update_data)
                        if result:
                            st.success("Задача обновлена!")
                            st.rerun()

        # Удаление задачи
        st.write("---")
        st.write("**🗑️ Удаление задачи**")
        col1, col2 = st.columns([3, 1])

        with col1:
            delete_task = st.selectbox("Выберите задачу для удаления", task_options, key="delete_task")

        with col2:
            if st.button("Удалить задачу", type="secondary"):
                task_id = int(delete_task.split(" - ")[0])
                if make_request(f"/tasks/{task_id}", "DELETE"):
                    st.success("Задача удалена!")
                    st.rerun()

    else:
        st.info("Задачи не найдены. Создайте первую задачу!")

    # Фильтрация задач
    st.subheader("🔍 Фильтры задач")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**📋 Задачи по проекту**")
        if projects:
            selected_project_filter = st.selectbox(
                "Выберите проект",
                [f"{p['id']} - {p['name']}" for p in projects],
                key="project_filter"
            )

            if selected_project_filter:
                project_id = int(selected_project_filter.split(" - ")[0])
                project_tasks = make_request(f"/tasks/project/{project_id}")

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
            selected_employee_filter = st.selectbox(
                "Выберите исполнителя",
                [f"{e['id']} - {e['name']} {e['surname']}" for e in employees],
                key="employee_filter"
            )

            if selected_employee_filter:
                employee_id = int(selected_employee_filter.split(" - ")[0])
                employee_tasks = make_request(f"/tasks/employee/{employee_id}")

                if employee_tasks:
                    st.write(f"Задачи сотрудника ({len(employee_tasks)}):")
                    for task in employee_tasks:
                        status_icon = "⏳" if task["status"] == "Новая" else "🔄" if task["status"] == "В работе" else "✅"
                        st.write(f"- {status_icon} {task['name']} (Статус: {task['status']})")
                else:
                    st.info("У этого сотрудника нет задач")


def main():
    """Главная функция приложения"""
    st.title("TaskTracker - Управление проектами, сотрудниками и задачами")

    # Боковая панель навигации
    st.sidebar.title("🧭 Навигация")
    page = st.sidebar.radio("Выберите раздел:", [
        "📋 Бэклог задач",
        "👥 Сотрудники",
        "🗂️ Проекты",
        "🔗 Назначения",
        "✅ Задачи",
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