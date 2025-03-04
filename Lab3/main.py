import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import os

def parse_table():
	# Запуск браузера (например, Chrome)
	driver = webdriver.Edge()
	driver.get("https://table.nsu.ru/group/23932")  # Замените на URL страницы с таблицей
	# Находим таблицу по классу
	table = driver.find_element(By.CSS_SELECTOR, "table.time-table")

	# 2. Считываем все строки таблицы (<tr>)
	rows = table.find_elements(By.TAG_NAME, "tr")

	# 3. Первая строка (rows[0]) содержит заголовки (<th>)
	headers = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, "th")]
	# Предполагаем, что получили: ["Время", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

	data = []

	# 4. Считываем данные из оставшихся строк (начиная со второй)
	for row in rows[1:]:
		# Получаем все ячейки в строке (<td>)
		cells = row.find_elements(By.TAG_NAME, "td")
		
		# Ожидаем, что ячеек будет ровно столько же, сколько заголовков
		if len(cells) == len(headers):
			row_data = []
			
			# a) Первая ячейка: "Время"
			time_cell = cells[0].text.strip()
			row_data.append(time_cell)
			
			# b) Остальные ячейки: Понедельник, Вторник, Среда, Четверг, Пятница, Суббота
			for day_cell in cells[1:]:
				# В одной ячейке может быть несколько занятий (несколько <div class="cell">)
				div_cells = day_cell.find_elements(By.CSS_SELECTOR, "div.cell")
				
				cell_contents = []
				for div_block in div_cells:
					# Извлекаем элементы внутри каждого <div class="cell">
					span_types = div_block.find_elements(By.CSS_SELECTOR, "span.type")
					subject_els = div_block.find_elements(By.CSS_SELECTOR, "div.subject")
					room_els    = div_block.find_elements(By.CSS_SELECTOR, "div.room")
					tutor_els   = div_block.find_elements(By.CSS_SELECTOR, "a.tutor")
					
					# Тип занятия (короткий текст + tooltip)
					if span_types:
						type_text = span_types[0].text.strip()
						type_tooltip = span_types[0].get_attribute("data-original-title") or ""
						# Сформируем строку вида "пр (практическое занятие)"
						if type_tooltip:
							type_line = f"{type_text} ({type_tooltip})"
						else:
							type_line = type_text
					else:
						type_line = ""
					
					# Название предмета
					subject_text = subject_els[0].text.strip() if subject_els else ""
					
					# Аудитория
					room_text = room_els[0].text.strip() if room_els else ""
					
					# Преподаватель
					tutor_text = tutor_els[0].text.strip() if tutor_els else ""
					
					# Собираем всё в многострочный блок
					block_content = "\n".join(filter(None, [
						type_line,
						subject_text,
						room_text,
						tutor_text
					]))
					
					# Если что-то есть, добавляем к списку занятий в ячейке
					if block_content:
						cell_contents.append(block_content)
				
				# Если занятий несколько, разделяем их " --- "
				day_text = "\n---\n".join(cell_contents) if cell_contents else ""
				row_data.append(day_text)
			
			data.append(row_data)

	# Закрываем браузер
	driver.quit()

	# 5. Формируем DataFrame из собранных данных
	df = pd.DataFrame(data, columns=headers)
	return df

def main():
	# Проверяем запускали ли мы сегодня скрипт
	today = datetime.date.today()
	week_day = today.weekday()
	cache_file = f"cache{week_day}.csv"
	res_table = None
	global class_times
	weekday_names = {0:'Понедельник',1:'Вторник', 2:'Среда', 3:'Четверг', 4:'Пятница', 5:'Суббота', 6:'Воскресенье' }

	if os.path.exists(cache_file):
		res_table = pd.read_csv(cache_file)
	else:
		res_table = parse_table()
		res_table.to_csv(cache_file)

	to_write_df = res_table[['Время', weekday_names[week_day]]]
	to_write_df.to_csv("schedule today.csv")
	print(to_write_df)


if __name__ == "__main__":
    main()