# Импорт всех необходимых модулей
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.utils.config import get_default_config
import time
 
config_dict = get_default_config()  # Инициализация get_default_config()
config_dict['language'] = 'ru'  # Установка языка
# Инициализация mgr.weather_at_place() И передача в качестве параметра туда страну и город
def get_weather(place):
    country = 'RU' #input("Введите код вашей страны: ")  # Переменная для записи страны/кода страны
    country_and_place = place + ", " + country  # Запись города и страны в одну переменную через запятую
 
    owm = OWM('1d7b448eb312d527659a388b580fc48e')  # Ваш ключ с сайта open weather map
    mgr = owm.weather_manager()  # Инициализация owm.weather_manager()
    observation = mgr.weather_at_place(country_and_place)  
    w = observation.weather
 
    status = w.detailed_status  # Узнаём статус погоды в городе и записываем в переменную status
    velocity = w.wind()['speed']  # Узнаем скорость ветра
    humidity = w.humidity  # Узнаём Влажность и записываем её в переменную humidity
    temp = w.temperature('celsius')['temp']  # Узнаём температуру в градусах по цельсию и записываем в переменную temp

    if velocity > 8 or abs(temp) > 30 :
        return 'Ужасная'
    if velocity > 5 or (humidity > 45 or humidity < 25) or abs(temp) > 25 :
        return 'Плохая'

    return 'Хорошая' 
if __name__ == '__main__':
    t1 = time.time()
    print(get_weather('Москва'))  # Вызов функции
    print(time.time() - t1)