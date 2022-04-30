from flask import Flask, request
import logging
import requests
import json
import os
from random import choice
from weather import get_weather
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

dialogs = {}


def get_agreement(req):
        if 'да' in req['request']['original_utterance'].lower():
            return True
        elif 'не' in req['request']['original_utterance'].lower():
            return False
        else:
            return None


def make_a_trip():
    pass

def get_walking_time(req):
    time = 0
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.NUMBER':
            time = int(entity['value'])
    if time == 0:
        return 'error'
    time_counting = req['request']['original_utterance'].split()[1].lower()
    if time_counting == 'минут':
        return time 
    elif time_counting in ['часа', 'часов']:
        return time * 60
    else:
        return 'error'


class Dialog():
    def __init__(self, user_id):
        self.stage = 1
        self.AUTH_TOKEN = 'OAuth AQAAAABFR7qRAAT7o-z5WS14-E3NgJ6iI4IoUeI'
        self.response = {
                        'session': request.json['session'],
                        'version': request.json['version'],
                        'response': {
                        'end_session': False
                                    }
                        }
        self.user_id = user_id
       
        
        self.response['response']['text'] = 'Привет! Добро пожаловать в навык "Вечерние Поездки". Скажите название своего города, чтобы начать поездку!'
        self.response['response']['tts'] = 'Привет! Добро пож+аловать в навык "Вечерние Поездки". Скаж+ите название своего города, чтобы начать поезтку!'
        self.response['response']['buttons'] = [{'title': 'Что ты умеешь?', 'hide': True},
                                                 {'title': 'Помощь', 'hide': True}] 
        return

        
    def make_dialog_line(self, req):
        self.update_response()
        if self.stage == 1:
            if req['request']['original_utterance'].lower() == 'что ты умеешь?':
                self.response['response']['text'] = 'Я могу предоставить сведения, которые могут оказаться полезными перед поездкой:\n Погода \n Состояние на дорогах.'
                self.response['response']['tts'] = 'Я могу предост+авить сведения, которые могут оказаца полезными перед поездкой, а именно sil <[150]> \n Погода sil <[150]> \n Состояние на дорогах. \n  Для этого просто скажите имя нужного вам города и улицу, на которую вы хотите проехать.'
                return
            self.city = self.get_city(req)
            if self.city is None:
                self.response['response']['text'] = 'Я не очень поняла вас'
            else:
                weather = get_weather(self.city)
                if weather == 'Хорошая':
                    self.response['response']['text'] = 'Отлично! Куда вы хотите поехать?'
                    self.stage = 3
                elif weather == 'Плохая':
                    self.response['response']['text'] = 'Хорошо, но хочу Вас предупредить, погода не очень хорошая. Не забудьте зонтик! Куда вы хотите поехать?'
                    self.stage = 3
                elif weather == 'Ужасная':
                    self.response['response']['text'] = 'Сомневаюсь, что это будет безопасная поездка, в такую погоду. Вы всё ещё уверены?'
                    self.stage = 2

            return

        elif self.stage == 2:

            agree_for_playing = get_agreement(req)
            if agree_for_playing is None:
                self.response['response']['text'] = 'Я не очень поняла вас'
            elif agree_for_playing:
                 self.response['response']['text'] = 'Если что, я вас предупреждала! Куда вы хотите поехать?'
            elif not agree_for_playing:
                self.response['response']['text'] = 'Наверное, так будет лучше. До свидания!'
                self.response['response']['end_session'] = True
                return
            self.make_info(street)
        
        elif self.stage == 3:
            street  = self.get_street(req)
            if street is None:
                self.response['response']['text'] = 'Я не очень поняла вас.'
            else:
                self.image_id = self.upload_image(street + self.city + '.png')['image']['id']
                self.response['response']['card'] = {}
                self.response['response']['card']['type'] = 'BigImage'
                self.response['response']['card']['title'] = f'Удачного пути! Цветными линиями обозначен уровень пробок.'
                self.response['response']['card']['image_id'] = self.image_id   
                self.response['response']['text'] = 'Ой'
                self.response['response']['end_session'] = True
                
            return


    def upload_image(self, image_name):
        with open(image_name, 'rb') as img:
            return requests.post('https://dialogs.yandex.net/api/v1/skills/f3760eb7-94ec-43f1-8d19-eb5a0ce1caa7/images', 
                     files={'file': (image_name, img)}, 
                     headers={'Authorization': self.AUTH_TOKEN}).json()


    def make_info(self, place):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        
        geocoder_params = {
                          "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                          "geocode": place,
                          "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
                  "featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        map_params = {
        "ll": f'{toponym_longitude},{toponym_lattitude}',
        "spn": f'0.005,0.005',
        "l": 'map,trf'
    }
        map_api_server = "http://static-maps.yandex.ru/1.x/"

        response = requests.get(map_api_server, params=map_params)
        
        with open(place + self.city + '.png', 'wb') as image:
            image.write(response.content)

    def get_city(self, req):
    # перебираем именованные сущности
        for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO то пытаемся получить город(city),
        # если нет, то возвращаем None
            if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
                return entity['value'].get('city', None)

    def get_response(self):
        return self.response


    def update_response(self):
        self.response = self.response = {
                        'session': request.json['session'],
                        'version': request.json['version'],
                        'response': {
                        'end_session': False
                                    }
                        }
    def get_street(self, req):
        for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO то пытаемся получить город(city),
        # если нет, то возвращаем None
            if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
                return entity['value'].get('street', None)

@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
     
    req = request.json
    user_id = user_id = req['session']['user_id']
    if req['session']['new']:
        dialogs[user_id] = Dialog(user_id)
        response = dialogs[user_id].get_response()
        return json.dumps(response)
    
    else:
        current_dialog = dialogs[user_id]
        current_dialog.make_dialog_line(req)
        response = dialogs[user_id].get_response()
        return json.dumps(response)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)