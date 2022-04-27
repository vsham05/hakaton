from flask import Flask, request
import logging
import requests
import json
import os
from random import choice
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


def get_weather():
    return  choice(['Хорошая', 'Плохая', 'Ужасная'])

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
        self.response = {
                        'session': request.json['session'],
                        'version': request.json['version'],
                        'response': {
                        'end_session': False
                                    }
                        }
        self.user_id = user_id
       
        
        self.response['response']['text'] = 'Привет! Добро пожаловать в навык "Прогулки с Алисой". Хотите прогуляться?'
        self.response['response']['buttons'] = [{'title': 'Что ты умеешь?', 'hide': True},
                                                 {'title': 'Помощь', 'hide': True}] 
        return

        
    def make_dialog_line(self, req):
        self.update_response()
        if self.stage == 1:
            if req['request']['original_utterance'].lower() == 'что ты умеешь?':
                self.response['response']['text'] = 'Я могу составить маршрут для вашей потенциальной прогулки, учитывая время, которое бы вы желали гулять. Также я буду предупреждать вас о возможном ухудшении погоды'
                return
            agree_for_playing = get_agreement(req)
            if agree_for_playing is None:
                self.response['response']['text'] = 'Я не очень поняла вас'
            elif agree_for_playing:
                weather = get_weather()
                if weather == 'Хорошая':
                    self.response['response']['text'] = 'Отлично! Сколько вы хотите погулять?'
                    self.stage = 3
                elif weather == 'Плохая':
                    self.response['response']['text'] = 'Хорошо, но хочу Вас предупредить, возможен небольшой дождь. Не забудьте зонтик! Сколько вы хотите погулять?'
                    self.stage = 3
                elif weather == 'Ужасная':
                    self.response['response']['text'] = 'Сомневаюсь, что это будет безопасная прогулка. Надвигается ураган. Вы всё ещё уверены?'
                    self.stage = 2
            elif not agree_for_playing:
                self.response['response']['text'] = 'Погуляем в следующий раз. До свидания!'
                self.response['response']['end_session'] = True

            return

        elif self.stage == 2:
            agree_for_playing = get_agreement(req)
            if agree_for_playing is None:
                self.response['response']['text'] = 'Я не очень поняла вас'
            elif agree_for_playing:
                 self.response['response']['text'] = 'Если что, я вас предупреждала! Сколько вы хотите погулять?'
            elif not agree_for_playing:
                self.response['response']['text'] = 'Наверное, так будет лучше. До свидания!'
                self.response['response']['end_session'] = True
        
        elif self.stage == 3:
            walking_time = get_walking_time(req)
            if walking_time == 'error':
                self.response['response']['text'] = 'Я не очень поняла вас'
            else:
                self.response['response']['text'] = 'Ваш маршрут готов!'
                trip = make_a_trip()
                self.response['response']['end_session'] = True
            return

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