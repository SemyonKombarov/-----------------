import csv

def csv_to_py_module(csv_file_path, output_py_file):
    """
    Конвертирует CSV файл в Python модуль в формате для функции csv_to_list
    Формат: ["значение2 (значение1)", "значение4 (значение3)"]
    """
    result_list = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Пропускаем заголовок
        for row in reader:
            if len(row) >= 2:
                # Формируем строку в нужном формате
                formatted_item = f'{row[1]} ({row[0]})'
                result_list.append(formatted_item)
    
    # Генерируем Python файл
    with open(output_py_file, 'w', encoding='utf-8') as py_file:
        py_file.write("# Этот модуль был автоматически сгенерирован\n")
        py_file.write("data = [\n")
        for item in result_list:
            # Экранируем кавычки в строке и оборачиваем в двойные кавычки
            escaped_item = item.replace('"', '\\"')
            py_file.write(f'    "{escaped_item}",\n')
        py_file.write("]\n")



# Пример использования
if __name__ == "__main__":
    csv_file_path = 'dictionary.csv'  # Замените на путь к вашему CSV файлу
    output_py_file = 'dictionary.py'  # Имя выходного Python файла
    
    csv_to_py_module(csv_file_path, output_py_file)
    print(f"Файл {output_py_file} успешно создан!")