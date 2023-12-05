import requests
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from tokenseim import access_token

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

bot_token = '***'
chat_id = ***


def send_message(message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, json=payload)
    return response.json()

def make_api_request():

    url = "https://<IP>/api/v2/incidents/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "offset": 0,
        "limit": 1,
        "groups": {
            "filterType": "no_filter"
        },
        "timeFrom": "2020-12-31T21:00:00.000Z",
        "timeTo": None,
        "filterTimeType": "creation",
        "filter": {
            "select": [
                "key",
                "name",
                "category",
                "type",
                "status",
                "created",
                "assigned",
                "severity"
            ],
            "where": "",
            "orderby": [
                {"field": "created", "sortOrder": "descending"},
                {"field": "status", "sortOrder": "ascending"},
                {"field": "severity", "sortOrder": "descending"}
            ]
        },
        "queryIds": ["all_incidents"]
    }

    response = requests.post(url, headers=headers, json=payload, verify=False)

    if response.status_code == 200:
        json_response = response.json()
        return json_response
    else:
        return f"Ошибка запроса с кодом состояния {response.status_code}"

def get_incident_details_by_id(incident_id):
    global current_access_token
    url = f"https://<IP>/api/incidentsReadModel/incidents/{incident_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        incident_details = response.json()
        #responce_target = incident_details.get("targets", "")
        #result_responce = foreach (target in responce_target){return $_.id + $_.name}
        formatted_details = {
            "<b>ID</b>": incident_details.get("id", ""),
            "<b>Номер инцидента</b>": incident_details.get("key", ""),
            "<b>Правило</b>": incident_details.get("name", ""),
            "<b>Описание</b>": incident_details.get("description", ""),
            "<b>Утвержден</b>": incident_details.get("isConfirmed", False),
            "<b>Статус</b>": incident_details.get("status", ""),
            "<b>Категория</b>": incident_details.get("category", ""),
            "<b>Важность</b>": incident_details.get("severity", ""),
            "<b>Тип</b>": incident_details.get("type", ""),
            "<b>Создан</b>": incident_details.get("created", ""),
            "<b>Обнаружен</b>": incident_details.get("detected", ""),
            "<b>Группа</b>": incident_details.get("group", ""),
            "<b>Цель</b>": ",\n" .join(extract_names_from_target(incident_details)),
            "<b>Атакующий</b>": ",\n".join(extract_names_from_attack(incident_details))
        }
        return formatted_details
    else:
        print(f"Error: {response.status_code}")
        return None
def get_incident_events_by_id(incident_id):
    global current_access_token
    url = f"https://<IP>/api/incidents/{incident_id}/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def extract_names_from_target(data):
    names_to_send = [asset['name'] for asset in data['targets']['assets']] + [other['name'] for other in data['targets']['others']]
    return names_to_send

def extract_names_from_attack(data):
    names_to_send2 = [asset['name'] for asset in data['attackers']['assets']] + [other['name'] for other in data['attackers']['others']]
    return names_to_send2

def format_incident(incident_data):
    incident_id = incident_data.get("id", "")
    incident_key = incident_data.get("key", "")
    incident_name = incident_data.get("name", "")
    rule = incident_data.get("category", "")
    #target = incident_data.get("targets:assets ", "")
    status = incident_data.get("status", "")
    category = incident_data.get("type", "")
    time = incident_data.get("created", "")

    formatted_output = f"<b>🚨Новый инцидент!</b>\n\n<b>ID:</b> <code>{incident_id}</code>\n\n<b>Номер инцидента:</b> {incident_key}\n\n<b>Правило:</b> {incident_name}\n\n<b>Тип:</b> {rule}\n\n<b>Категория:</b> {category}\n\n<b>Время:</b> {time}\n\n"
    return formatted_output
def parse_incident_events_to_string(events):
    event_info = ""

    if events:
        for event in events:
            event_id = event.get("id", "")
            event_type = event.get("type", "")
            event_description = event.get("description", "")
            event_time = event.get("timestamp", "")

            event_info += f"ID события: {event_id}\n\n"
            event_info += f"Тип события: {event_type}\n\n"
            event_info += f"Описание события: {event_description}\n\n"
            event_info += f"Время события: {event_time}\n\n"
            event_info += "------------------------------------------\n\n"
    else:
        event_info = "Нет событий для данного инцидента."

    return event_info


def send_message_with_inline_keyboard_and_callback(message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    keyboard = {
        "inline_keyboard": [
            [{"text": "Подробнее", "callback_data": "more_info"}],
            [{"text": "События", "callback_data": "events"}]
        ]
    }
    payload = {
        'chat_id': chat_id,
        'text': message,
        'reply_markup': keyboard,
        'parse_mode': 'HTML'  # Разрешить HTML-разметку для кнопок
    }
    response = requests.post(url, json=payload)
    return response.json()


def send_incident_details(chat_id, incident_details):
    formatted_details = "\nДетальная информация:\n"
    for key, value in incident_details.items():
        formatted_details += f"{key}: {value}\n"

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': formatted_details,
        'parse_mode': 'HTML'  # Разрешить HTML-разметку
    }
    response = requests.post(url, json=payload)
    return response.json()

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data == 'more_info':
        # Подробная информация о инциденте
        incident_id = previous_incident_id  # Идентификатор последнего инцидента
        incident_details = get_incident_details_by_id(incident_id)
        if incident_details:
            send_incident_details(chat_id, incident_details)
            # Добавляем кнопку "Назад"
            keyboard = [[InlineKeyboardButton("Назад", callback_data='back_to_incident')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.message.reply_text('Вы просматриваете детальную информацию.', reply_markup=reply_markup)
        else:
            send_message("Не удалось получить детали инцидента.")

    elif data == 'events':
        # Первые 5 событий инцидента
        incident_id = previous_incident_id  # Идентификатор последнего инцидента
        incident_events = get_incident_events_by_id(incident_id)
        if incident_events:
            events_info = parse_incident_events_to_string(incident_events[:5])  # Получение первых 5 событий
            send_message(events_info)
            # Добавляем кнопку "Назад"
            keyboard = [[InlineKeyboardButton("Назад", callback_data='back_to_incident')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.message.reply_text('Вы просматриваете события.', reply_markup=reply_markup)
        else:
            send_message("Нет событий для данного инцидента.")

    elif data == 'back_to_incident':
        # Отображаем информацию о последнем инциденте снова
        formatted_data = format_incident(api_response['incidents'][0])  # Получаем информацию о последнем инциденте
        send_message_with_inline_keyboard_and_callback(formatted_data)

updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CallbackQueryHandler(button_callback))

updater.start_polling()

# Инициализация предыдущего ID (можно начать с пустого значения)
previous_incident_id = ""
def send_incident_events(chat_id, incident_id):
    incident_events = get_incident_events_by_id(incident_id)
    events_info = parse_incident_events_to_string(incident_events)
    send_message(events_info)

while True:
    api_response = make_api_request()

    if isinstance(api_response, dict) and 'incidents' in api_response and api_response['incidents']:
        current_incident_id = api_response['incidents'][0].get("id", "")

        if current_incident_id != previous_incident_id:
            formatted_data = format_incident(api_response['incidents'][0])

            # Отправка уведомления в Телеграм с кнопками
            send_message_with_inline_keyboard_and_callback(formatted_data)
            previous_incident_id = current_incident_id
    time.sleep(10)  # Пауза в 10 секунд перед следующим запросом к API
updater.idle()