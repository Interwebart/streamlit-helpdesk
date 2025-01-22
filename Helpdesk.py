import streamlit as st
import os
import json
from datetime import datetime
from dateutil.parser import parse

# Устанавливаем широкий режим
st.set_page_config(
    page_title="Bug Tracker",
    layout="wide",  # Включаем широкий режим
    initial_sidebar_state="expanded",  # Боковая панель развернута
)

# Создание папки для хранения тикетов
TICKET_FOLDER = "ticket"
os.makedirs(TICKET_FOLDER, exist_ok=True)

# Функция для загрузки всех карточек
def load_tickets():
    tickets = []
    for filename in os.listdir(TICKET_FOLDER):
        if filename.endswith(".json"):
            with open(os.path.join(TICKET_FOLDER, filename), "r") as f:
                ticket = json.load(f)
                ticket["filename"] = filename  # Добавляем имя файла для идентификации
                ticket["timestamp"] = datetime.strptime(ticket.get("timestamp", datetime.now().isoformat()), "%Y-%m-%dT%H:%M:%S.%f")
                tickets.append(ticket)
    return sorted(tickets, key=lambda x: x["timestamp"], reverse=True)  # Сортируем по времени

# Функция для сохранения карточки
def save_ticket(ticket, filename=None):
    if not filename:
        filename = f"{ticket['username']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    ticket["timestamp"] = datetime.now().isoformat()  # Добавляем временную метку
    filepath = os.path.join(TICKET_FOLDER, filename)
    with open(filepath, "w") as f:
        json.dump(ticket, f, indent=4)

# Проверяем, загружены ли тикеты в session_state
if "tickets" not in st.session_state:
    st.session_state.tickets = load_tickets()

# Боковая панель для создания карточки
st.sidebar.title("Создание карточки")
username = st.sidebar.text_input("Имя пользователя", value="")
date = st.sidebar.date_input("Дата", value=datetime.today())
description = st.sidebar.text_area("Описание бага", value="")
priority = st.sidebar.selectbox(
    "Критичность",
    options=["Зеленый (Low)", "Желтый (Medium)", "Красный (High)", "Черный (Critical)"],
)

# Цветовая схема для карточек
priority_colors = {
    "Зеленый (Low)": "#90EE90",
    "Желтый (Medium)": "#FFD700",
    "Красный (High)": "#FF4500",
    "Черный (Critical)": "#000000",
    "RESOLVED": "#FFFFFF",  # Цвет для решенных тикетов
}

if st.sidebar.button("Сохранить карточку"):
    if username and description:
        # Создаем карточку
        ticket = {
            "username": username,
            "date": str(date),
            "description": description,
            "priority": priority,
            "status": "OPEN",  # Новый тикет по умолчанию открыт
            "timestamp": datetime.now().isoformat(),  # Временная метка
        }
        save_ticket(ticket)
        st.session_state.tickets.insert(0, ticket)  # Добавляем в начало списка
        st.sidebar.success("Карточка сохранена!")
    else:
        st.sidebar.error("Имя пользователя и описание обязательны!")

# Центральное окно для отображения карточек
st.title("Список карточек")

tickets = st.session_state.tickets
if tickets:
    for ticket in tickets:
        # Проверяем наличие обязательных полей
        ticket["priority"] = ticket.get("priority", "Зеленый (Low)")
        ticket["status"] = ticket.get("status", "OPEN")

        color = (
            priority_colors[ticket["priority"]]
            if ticket["status"] == "OPEN"
            else priority_colors["RESOLVED"]
        )

        # Обработка времени
        timestamp = ticket.get("timestamp", None)
        if timestamp:
            try:
                formatted_time = parse(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                formatted_time = "Некорректное время"
        else:
            formatted_time = "Время не указано"

        # Создаем карточку
        col1, col2 = st.columns([10, 1])  # Разделяем на карточку и кнопку
        with col1:
            st.markdown(
                f"""
                <div style="border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px; padding: 10px; background-color: {color};">
                    <h4 style="margin: 0;">{ticket['username']}</h4>
                    <p style="margin: 0;"><b>Дата:</b> {ticket['date']}</p>
                    <p style="margin: 0;"><b>Время:</b> {formatted_time}</p>
                    <p style="margin: 0;"><b>Описание:</b> {ticket['description']}</p>
                    <p style="margin: 0;"><b>Критичность:</b> {ticket['priority']}</p>
                    <p style="margin: 0;"><b>Статус:</b> {"РЕШЕН" if ticket["status"] == "RESOLVED" else "ОТКРЫТ"}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            if ticket.get("status", "OPEN") == "OPEN" and st.button("RESOLVED", key=f"resolved-{ticket.get('filename', '')}"):
                ticket["status"] = "RESOLVED"
                save_ticket(ticket, ticket["filename"])  # Обновляем файл
                st.session_state.tickets = tickets  # Обновляем состояние
else:
    st.info("Карточки отсутствуют. Создайте новую карточку на боковой панели!")