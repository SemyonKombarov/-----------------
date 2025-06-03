import os, re, csv

def get_file_list(folder_path):
    """
    Возвращает список названий файлов в указанной папке
    
    :param folder_path: Путь к папке
    :return: Список названий файлов
    """
    try:
        # Получаем список всех элементов в папке
        all_items = os.listdir(folder_path)
        
        # Фильтруем, оставляя только файлы (исключаем папки)
        file_list = [item for item in all_items if os.path.isfile(os.path.join(folder_path, item))]
        
        return file_list
    
    except FileNotFoundError:
        print(f"Ошибка: Папка '{folder_path}' не найдена.")
        return []
    except PermissionError:
        print(f"Ошибка: Нет доступа к папке '{folder_path}'.")
        return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

def csv_to_dict(filename):
    result_dict = {}
    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Пропускаем заголовок (если он есть)
        for row in reader:
            if len(row) >= 2:  # Проверяем, что строка содержит ключ и значение
                key, value = row[0], row[1]
                result_dict[key] = value
    return result_dict

# Пример использования
loaded_dict = csv_to_dict('dictionary.csv')
print(loaded_dict)

# Пример использования
if __name__ == "__main__":
    dct = dict()
    path = "C:/Users/semyo/OneDrive/Desktop/Перевод координат/EPSG-v12_013-WKT"
    files = get_file_list(path)
    y = 0
    for file in files:
        if str(file).startswith("EPSG-CRS"):
            y += 1
            x = re.findall(r"-(\d+)\.wkt",file)
            # print(x)
            path_file = path + "/" + file
            with open(path_file, 'r', encoding='utf-8') as file:
                wkt_data = file.read()
                match = re.search(r'"([^"]*)"',wkt_data)
                if match:
                    first_quoted_text = match.group(1)
                dct[x[0]] = first_quoted_text
    with open('dictionary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Key', 'Value'])  # Заголовок (опционально)
        for key, value in dct.items():
            writer.writerow([key, value])
    
    
    loaded_dict = csv_to_dict('dictionary.csv')
    print(loaded_dict)
    
            
                