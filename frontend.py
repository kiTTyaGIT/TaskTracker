import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Конфигурация
API_BASE_URL = "http://localhost:8090"
st.set_page_config(page_title="TaskTracker", layout="wide")


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


def show_projects_page():
    st.header("📋 Управление проектами")

    # Создание нового проекта
    with st.expander("➕ Создать новый проект"):
        with st.form("create_project"):
            name = st.text_input("Название проекта")
            description = st.text_area("Описание")
            start_date = st.date_input("Дата начала")
            finish_date = st.date_input("Дата окончания")

            if st.form_submit_button("Создать проект"):
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

    # Список проектов
    st.subheader("Список проектов")
    projects = make_request("/projects/")

    if projects:
        # Преобразуем в DataFrame для красивого отображения
        projects_df = pd.DataFrame(projects)
        st.dataframe(projects_df, use_container_width=True)

        # Редактирование и удаление проектов
        st.subheader("Управление проектами")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Редактировать проект**")
            project_names = [p["name"] for p in projects]
            selected_project = st.selectbox("Выберите проект", project_names, key="edit_project")

            if selected_project:
                project = next((p for p in projects if p["name"] == selected_project), None)
                if project:
                    with st.form("edit_project_form"):
                        new_name = st.text_input("Название", value=project["name"])
                        new_description = st.text_area("Описание", value=project["description"] or "")

                        if st.form_submit_button("Обновить проект"):
                            update_data = {
                                "name": new_name,
                                "description": new_description
                            }
                            result = make_request(f"/projects/{selected_project}", "PUT", update_data)
                            if result:
                                st.success("Проект обновлен!")
                                st.rerun()

        with col2:
            st.write("**Удалить проект**")
            delete_project = st.selectbox("Выберите проект для удаления", project_names, key="delete_project")
            if st.button("Удалить проект", type="secondary"):
                if make_request(f"/projects/{delete_project}", "DELETE"):
                    st.success("Проект удален!")
                    st.rerun()


def show_employees_page():
    st.header("👥 Управление сотрудниками")

    # Создание нового сотрудника
    with st.expander("➕ Добавить сотрудника"):
        with st.form("create_employee"):
            name = st.text_input("Имя")
            surname = st.text_input("Фамилия")
            patronymic = st.text_input("Отчество")
            phone_number = st.text_input("Телефон")
            mail = st.text_input("Email")

            if st.form_submit_button("Добавить сотрудника"):
                employee_data = {
                    "name": name,
                    "surname": surname,
                    "patronymic": patronymic,
                    "phone_number": phone_number,
                    "mail": mail
                }
                result = make_request("/employees/", "POST", employee_data)
                if result:
                    st.success("Сотрудник успешно добавлен!")
                    st.rerun()

    # Список сотрудников
    st.subheader("Список сотрудников")
    employees = make_request("/employees/")

    if employees:
        employees_df = pd.DataFrame(employees)
        st.dataframe(employees_df, use_container_width=True)

        # Редактирование и удаление сотрудников
        st.subheader("Управление сотрудниками")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Редактировать сотрудника**")
            employee_ids = [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]
            selected_employee = st.selectbox("Выберите сотрудника", employee_ids, key="edit_employee")

            if selected_employee:
                employee_id = int(selected_employee.split(" - ")[0])
                employee = next((e for e in employees if e["id"] == employee_id), None)
                if employee:
                    with st.form("edit_employee_form"):
                        new_name = st.text_input("Имя", value=employee["name"])
                        new_surname = st.text_input("Фамилия", value=employee["surname"])
                        new_patronymic = st.text_input("Отчество", value=employee["patronymic"] or "")
                        new_phone = st.text_input("Телефон", value=employee["phone_number"] or "")
                        new_mail = st.text_input("Email", value=employee["mail"] or "")

                        if st.form_submit_button("Обновить сотрудника"):
                            update_data = {
                                "name": new_name,
                                "surname": new_surname,
                                "patronymic": new_patronymic,
                                "phone_number": new_phone,
                                "mail": new_mail
                            }
                            result = make_request(f"/employees/{employee_id}", "PUT", update_data)
                            if result:
                                st.success("Данные сотрудника обновлены!")
                                st.rerun()

        with col2:
            st.write("**Удалить сотрудника**")
            delete_employee = st.selectbox("Выберите сотрудника для удаления", employee_ids, key="delete_employee")
            if st.button("Удалить сотрудника", type="secondary"):
                employee_id = int(delete_employee.split(" - ")[0])
                if make_request(f"/employees/{employee_id}", "DELETE"):
                    st.success("Сотрудник удален!")
                    st.rerun()


def show_assignments_page():
    st.header("🔗 Назначения сотрудников на проекты")

    # Получаем данные
    employees = make_request("/employees/")
    projects = make_request("/projects/")

    if not employees or not projects:
        st.error("Не удалось загрузить данные")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Добавить сотрудника в проект")
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

    with col2:
        st.subheader("Удалить сотрудника из проекта")
        with st.form("remove_assignment"):
            # Получаем текущие назначения
            assignments = make_request("/employee-projects/")
            if assignments:
                assignment_options = [
                    f"Сотрудник {a['employee_id']} -> Проект {a['project_id']}"
                    for a in assignments
                ]

                selected_assignment = st.selectbox("Выберите назначение", assignment_options)

                if st.form_submit_button("Удалить из проекта"):
                    employee_id = int(selected_assignment.split("Сотрудник ")[1].split(" ->")[0])
                    project_id = int(selected_assignment.split("Проект ")[1])

                    if make_request(f"/employee-projects/?employee_id={employee_id}&project_id={project_id}", "DELETE"):
                        st.success("Сотрудник удален из проекта!")

    # Просмотр назначений
    st.subheader("Текущие назначения")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Проекты и их сотрудники**")
        selected_project_view = st.selectbox(
            "Выберите проект",
            [f"{p['id']} - {p['name']}" for p in projects],
            key="project_view"
        )

        if selected_project_view:
            project_id = int(selected_project_view.split(" - ")[0])
            project_employees = make_request(f"/employee-projects/projects/{project_id}/employees")
            if project_employees:
                employees_df = pd.DataFrame(project_employees["employees"])
                st.dataframe(employees_df, use_container_width=True)

    with col2:
        st.write("**Сотрудники и их проекты**")
        selected_employee_view = st.selectbox(
            "Выберите сотрудника",
            [f"{e['id']} - {e['name']} {e['surname']}" for e in employees],
            key="employee_view"
        )

        if selected_employee_view:
            employee_id = int(selected_employee_view.split(" - ")[0])
            employee_projects = make_request(f"/employee-projects/employees/{employee_id}/projects")
            if employee_projects:
                projects_df = pd.DataFrame(employee_projects["projects"])
                st.dataframe(projects_df, use_container_width=True)


def show_overview_page():
    st.header("📈 Обзор системы")

    # Статистика
    employees = make_request("/employees/")
    projects = make_request("/projects/")
    assignments = make_request("/employee-projects/")
    tasks = make_request("/tasks/")

    if employees and projects:
        col1, col2, col3, col4 = st.columns(4)  # Добавлен четвертый столбец

        with col1:
            st.metric("Всего сотрудников", len(employees))
        with col2:
            st.metric("Всего проектов", len(projects))
        with col3:
            st.metric("Всего назначений", len(assignments) if assignments else 0)
        with col4:  # Добавлено
            st.metric("Всего задач", len(tasks) if tasks else 0)

    # Статистика по задачам
    if tasks:
        st.subheader("📊 Статистика задач")

        col1, col2, col3 = st.columns(3)

        # Подсчет задач по статусам
        status_counts = {}
        for task in tasks:
            status = task.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        with col1:
            pending = status_counts.get('pending', 0)
            st.metric("⏳ Ожидает", pending)

        with col2:
            in_progress = status_counts.get('in_progress', 0)
            st.metric("🔄 В работе", in_progress)

        with col3:
            completed = status_counts.get('completed', 0)
            st.metric("✅ Завершено", completed)

    # Визуализация
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Сотрудники по проектам")
        if projects and assignments:
            project_assignments = {}
            for project in projects:
                project_employees = make_request(f"/employee-projects/projects/{project['id']}/employees")
                if project_employees:
                    project_assignments[project['name']] = len(project_employees['employees'])

            if project_assignments:
                chart_data = pd.DataFrame({
                    'Проекты': list(project_assignments.keys()),
                    'Количество сотрудников': list(project_assignments.values())
                })
                st.bar_chart(chart_data.set_index('Проекты'))

    with col2:
        st.subheader("Последние задачи")
        tasks_with_details = make_request("/tasks/with-details")
        if tasks_with_details:
            recent_tasks = sorted(tasks_with_details, key=lambda x: x.get('id', 0), reverse=True)[:5]
            for task in recent_tasks:
                status_icon = "⏳" if task["status"] == "pending" else "🔄" if task["status"] == "in_progress" else "✅"
                with st.expander(f"{status_icon} {task['name']}"):
                    st.write(f"**Проект:** {task.get('project_name', 'Неизвестно')}")
                    st.write(f"**Исполнитель:** {task.get('employee_name', 'Не назначен')}")
                    st.write(f"**Часы:** {task.get('needed_hours', 'Не указано')}")
                    st.write(f"**Статус:** {task['status']}")


def show_tasks_page():
    st.header("✅ Управление задачами")

    # Создание новой задачи
    with st.expander("➕ Создать новую задачу"):
        with st.form("create_task"):
            # Получаем проекты и сотрудников для выбора
            projects = make_request("/projects/")
            employees = make_request("/employees/")

            if projects and employees:
                project_options = [f"{p['id']} - {p['name']}" for p in projects]
                employee_options = ["Не назначено"] + [f"{e['id']} - {e['name']} {e['surname']}" for e in employees]

                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Название задачи*")
                    selected_project = st.selectbox("Проект*", project_options)
                    needed_hours = st.number_input("Необходимо часов", min_value=0, value=0)

                with col2:
                    description = st.text_area("Описание")
                    selected_employee = st.selectbox("Исполнитель", employee_options)
                    status = st.selectbox("Статус", ["pending", "in_progress", "completed"])

                if st.form_submit_button("Создать задачу"):
                    if not name:
                        st.error("Название задачи обязательно!")
                    else:
                        task_data = {
                            "name": name,
                            "description": description,
                            "needed_hours": needed_hours,
                            "status": status,
                            "project_id": int(selected_project.split(" - ")[0]),
                            "employee_id": int(
                                selected_employee.split(" - ")[0]) if selected_employee != "Не назначено" else None
                        }
                        result = make_request("/tasks/", "POST", task_data)
                        if result:
                            st.success("Задача успешно создана!")
                            st.rerun()
            else:
                st.error("Не удалось загрузить данные проектов и сотрудников")

    # Просмотр задач с деталями
    st.subheader("📋 Список задач")

    tasks_with_details = make_request("/tasks/with-details")

    if tasks_with_details:
        # Создаем DataFrame для отображения
        tasks_df = pd.DataFrame(tasks_with_details)

        # Переименовываем колонки для лучшего отображения
        display_df = tasks_df[
            ['id', 'name', 'description', 'needed_hours', 'status', 'employee_name', 'project_name']].copy()
        display_df.columns = ['ID', 'Название', 'Описание', 'Часы', 'Статус', 'Исполнитель', 'Проект']

        # Заменяем None значения
        display_df['Исполнитель'] = display_df['Исполнитель'].fillna('Не назначен')
        display_df['Описание'] = display_df['Описание'].fillna('Нет описания')

        # Красивое отображение статусов
        status_icons = {
            'pending': '⏳ Ожидает',
            'in_progress': '🔄 В работе',
            'completed': '✅ Завершена'
        }
        display_df['Статус'] = display_df['Статус'].map(status_icons).fillna(display_df['Статус'])

        st.dataframe(display_df, use_container_width=True)

        # Управление задачами
        st.subheader("⚙️ Управление задачами")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Назначить исполнителя**")
            task_options = [f"{t['id']} - {t['name']}" for t in tasks_with_details]
            selected_task_assign = st.selectbox("Выберите задачу", task_options, key="assign_task")

            if selected_task_assign:
                employee_options = ["Снять назначение"] + [f"{e['id']} - {e['name']} {e['surname']}" for e in
                                                           make_request("/employees/") or []]
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
            st.write("**Изменить статус**")
            selected_task_status = st.selectbox("Выберите задачу", task_options, key="status_task")

            if selected_task_status:
                new_status = st.selectbox("Новый статус",
                                          ["pending", "in_progress", "completed"],
                                          format_func=lambda x: {
                                              "pending": "⏳ Ожидает",
                                              "in_progress": "🔄 В работе",
                                              "completed": "✅ Завершена"
                                          }[x])

                if st.button("Обновить статус"):
                    task_id = int(selected_task_status.split(" - ")[0])
                    result = make_request(f"/tasks/{task_id}/status?status={new_status}", "PATCH")
                    if result:
                        st.success("Статус обновлен!")
                        st.rerun()

        with col3:
            st.write("**Редактировать задачу**")
            selected_task_edit = st.selectbox("Выберите задачу", task_options, key="edit_task")

            if selected_task_edit:
                task_id = int(selected_task_edit.split(" - ")[0])
                task = next((t for t in tasks_with_details if t['id'] == task_id), None)

                if task:
                    with st.form("edit_task_form"):
                        new_name = st.text_input("Название", value=task["name"])
                        new_description = st.text_area("Описание", value=task["description"] or "")
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
        st.write("**Задачи по проекту**")
        projects = make_request("/projects/")
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
                        status_icon = "⏳" if task["status"] == "pending" else "🔄" if task[
                                                                                         "status"] == "in_progress" else "✅"
                        st.write(f"- {status_icon} {task['name']} (Часы: {task['needed_hours'] or 'не указано'})")
                else:
                    st.info("В этом проекте нет задач")

    with col2:
        st.write("**Задачи по исполнителю**")
        employees = make_request("/employees/")
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
                        status_icon = "⏳" if task["status"] == "pending" else "🔄" if task[
                                                                                         "status"] == "in_progress" else "✅"
                        st.write(f"- {status_icon} {task['name']} (Статус: {task['status']})")
                else:
                    st.info("У этого сотрудника нет задач")


def main():
    st.title("📊 TaskTracker - Управление проектами, сотрудниками и задачами")

    # Боковая панель навигации
    st.sidebar.title("Навигация")
    page = st.sidebar.radio("Выберите раздел:", [
        "Проекты",
        "Сотрудники",
        "Назначения",
        "Задачи",  # Добавлено
        "Обзор"
    ])

    if page == "Проекты":
        show_projects_page()
    elif page == "Сотрудники":
        show_employees_page()
    elif page == "Назначения":
        show_assignments_page()
    elif page == "Задачи":  # Добавлено
        show_tasks_page()
    elif page == "Обзор":
        show_overview_page()

if __name__ == "__main__":
    main()