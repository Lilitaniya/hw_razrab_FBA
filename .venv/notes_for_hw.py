import easygui
import sqlite3
import json
import csv
# подключение к базе данных SQLite
def connect_to_sqlite():
    conn = sqlite3.connect('notes_db.sqlite')
    return conn
# Создание таблицы заметок
def create_notes_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, body TEXT)")
        conn.commit()
    except Exception as e:
        print(f"Ошибка создания таблицы: {e}")
# Создание самой заметки
def create_note():
    title = easygui.enterbox("Заголовок заметки:")
    body = easygui.enterbox("Текст заметки:")
    note = {
        'title': title,
        'body': body
    }
    return note
# Сохранение заметки в базе данных SQLite
def save_note_to_sqlite(note, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (note['title'], note['body']))
        conn.commit()
    except Exception as e:
        print(f"Ошибка сохранения заметки: {e}")
# Отображение списка заметок
def display_notes(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes")
        result = cursor.fetchall()
        for row in result:
            easygui.msgbox(f"Заголовок: {row[1]}\nТекст: {row[2]}")
    except Exception as e:
        print(f"Ошибка отображения заметок:{e}")
# Импорт заметок из CSV файла в базу данных SQLite
def import_notes_from_csv(file_name, conn):
    try:
        with open(file_name, "r") as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (row[0], row[1]))
                conn.commit()
    except Exception as e:
        print(f"Ошибка импорта из CSV: {e}")
# Импорт заметок из JSON файла в базу данных SQLite
def import_notes_from_json(file_name, conn):
    try:
        with open(file_name, "r") as file:
            notes = json.load(file)
            cursor = conn.cursor()
            for note in notes:
                cursor.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (note['title'], note['body']))
            conn.commit()
        easygui.msgbox(f"{len(notes)} Заметки импортированы из JSON!")
    except Exception as e:
        print(f"Ошибка импорта из JSON: {e}")
# Редактирование заметки по ее ID (номер по порядку)
def edit_note_by_id(note_id, conn):
    note = get_note_by_id(note_id, conn)
    if note is None:
        return

    new_title = easygui.enterbox("Новый заголовок заметки:", default=note[1])
    new_body = easygui.enterbox("Новый текст заметки:", default=note[2])

    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE notes SET title = ?, body = ? WHERE id = ?", (new_title, new_body, note_id))
        conn.commit()
        easygui.msgbox("Заметка успешно отредактирована!")
    except Exception as e:
        print(f"Ошибка редактирования заметки: {e}")
# Получение заметки по ее ID
def get_note_by_id(note_id, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Ошибка получения заметки по ID: {e}")
        return None
# Изменение заметки по ее названию
def edit_note_by_title(note_title, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE title = ?", (note_title,))
        result = cursor.fetchone()
        if result is None:
            easygui.msgbox("Заметка с таким названием не найдена!")
            return
        note_id = result[0]
        new_title = easygui.enterbox("Новый заголовок заметки:", default=result[1])
        new_body = easygui.enterbox("Новый текст заметки:", default=result[2])

        cursor.execute("UPDATE notes SET title = ?, body = ? WHERE id = ?", (new_title, new_body, note_id))
        conn.commit()
        easygui.msgbox("Заметка успешно отредактирована!")
    except Exception as e:
        print(f"Ошибка редактирования заметки: {e}")

def delete_note_by_id(note_id, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        cursor.execute("SELECT * FROM notes")
        display_notes(cursor)
        cursor.close()
        easygui.msgbox("Заметка была удалена.")
    except Exception as e:
        print(f"Ошибка удаления заметки: {e}")


# Подключение к базе данных SQLite
conn = connect_to_sqlite()
# Создание таблицы заметок
create_notes_table(conn)
# Основной цикл программы
while True:
    choices = ["Создать заметку", "Показать заметки", "Изменить заметку по ID", "Edit Note by Title", "Delete Note", "CSV import", "JSON import", "Exit"]
    choice = easygui.buttonbox("Select an action:", choices=choices)
    if choice == "Создать заметку":
        note = create_note()
        save_note_to_sqlite(note, conn)
    elif choice == "Показать заметки":
        display_notes(conn)
    elif choice == "Изменить заметку по ID":
        note_id = easygui.enterbox("Введите ID заметки для редактирования:")
        edit_note_by_id(note_id, conn)
    elif choice == "Edit Note by Title":
        note_title = easygui.enterbox("Введите название заметки для редактирования:")
        edit_note_by_title(note_title, conn)
    elif choice == "Delete Note":
        note_id = easygui.enterbox("Введите ID заметки для удаления:")
        delete_note_by_id(note_id, conn)
    elif choice == "CSV import":
        file_name = easygui.fileopenbox("Select a CSV file to import:")
        import_notes_from_csv(file_name, conn)
    elif choice == "JSON import":
        file_name = easygui.fileopenbox("Select a JSON file to import:")
        import_notes_from_json(file_name, conn)
    elif choice == "Exit":
        conn.close()
        break