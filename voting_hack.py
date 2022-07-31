import random
import sys
import json
import threading
import requests
from fake_headers import Headers
header = Headers(
    headers=True
)
banner = """ _  _    _     _  _    _     ___  _   _  _  _ 
| || |  /_\   | || |  /_\   | __|| | | || \| |
| __ | / _ \  | __ | / _ \  | _| | |_| || .` |
|_||_|/_/ \_\ |_||_|/_/ \_\ |_|   \___/ |_|\_|
"""


def start():
    print(banner)
    print("Mentimeter Multiple choice spammer")
    print("----------------------------------")
    # Если чел не указал ссылку
    if len(sys.argv) < 2:
        print(f"\n( `ε´ ) you need to provide the menti page, ex: https://www.menti.com/uyupv3tww7")
        sys.exit(1)
    else:
        sys.argv[1] = str(sys.argv[1]).replace('https', 'http')
    if len(sys.argv) < 3:
        print('Промежуток времени выбран', 2, 'мин.')
        minutes = 2
    else:
        minutes = int(sys.argv[2])
    TARGET = sys.argv[1]
    KEY = TARGET.split('/',)[3]  # Получаем код голосования из ссылки
    SUPPORTED_TYPE = ['choices', 'ranking', 'wordcloud', 'open', 'scales', 'qfa', 'prioritisation', 'rating']
    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": header.generate()['User-Agent']
    }
    # Получаем инфу о голосовании
    firstPage = requests.get(f"https://www.menti.com/core/vote-keys/{KEY}/series", headers=HEADERS)
    # Обрываем если инфа не доступна
    if firstPage.status_code != 200:
        print(f"{firstPage.status_code} WTF I can't access the page (＃`Д´)")
        print(f"{firstPage.text}")
        sys.exit(1)
    INIT = firstPage.json()
    PRESENTER_ID = INIT['pace']['active']
    PRESENTER_QUESTION = INIT['questions'][0]  # default
    # Проверям доступен ли тип голосования
    for question in INIT['questions']:
        if PRESENTER_ID == question['id']:
            if question['type'] not in SUPPORTED_TYPE:
                print(f"Черт возьми, это{question['type']}, разве я не говорил тебе, что это только для {SUPPORTED_TYPE}? (＃`Д´)")
                print(f"Просто подождите, пока ведущий не покажет {SUPPORTED_TYPE} голосовать!")
                sys.exit(1)
            PRESENTER_QUESTION = question
            break

    # id ответов и их содержимое
    pqi = {f"{item['id']}": item['label'] for item in PRESENTER_QUESTION['choices']}
    # CURRENT_ID = INIT['pace']['active']
    # id вопросв и их содержимое
    QUESTIONS = {question['id']: question for question in INIT['questions']}
    print('Тип вопросов', QUESTIONS[PRESENTER_ID]['type'])
    if QUESTIONS[PRESENTER_ID]['type'] == "qfa":
        page = 0
        parseQA = []
        while True:
            page += 1
            getQA = requests.get(f"https://www.menti.com/core/vote-keys/{KEY}/qfa?page={page}", headers=HEADERS)
            dataQA = getQA.json()
            parseQA += [item for item in dataQA['data']]
            if len(dataQA['data']) == 0:
                break
        for q in parseQA:
            print(f"ID {q['id']} {q['question']}")
    else:
        for choice in PRESENTER_QUESTION['choices']:
            print(f"ID {choice['id']} LABEL {choice['label']}")

    value = ""
    if QUESTIONS[PRESENTER_ID]['type'] in ['wordcloud', 'open']:
        choice = input(f"\nКакой текст вы хотите отправить: ")
    elif QUESTIONS[PRESENTER_ID]['type'] == "scales":
        choice = input(f"\nЗа какой ID вы хотите проголосовать: ")
        while True:
            value = input(f"\nВставьте значение: ")
            value = int(value)
            # if value < 0 or value > 10:
            #     print("ВТФ? повторный ввод mf")
            # else:
            #     reValue = [value, 1]
            value = {
                f"{choice}": value
            }
            break
    elif QUESTIONS[PRESENTER_ID]['type'] == "rating":
        choice = input(f"\nWhich ID you want to vote: ")
        while True:
            valueHorizontal = input(f"\nInsert horizontal axis value from 1-10: ")
            valueHorizontal = int(valueHorizontal)
            if valueHorizontal < 0 or valueHorizontal > 10:
                print("WTF? re-input mf")
            else:
                valueVertical = input(f"Insert vertical axis value from 1-10: ")
                valueVertical = int(valueVertical)
                if valueVertical < 0 or valueVertical > 10:
                    print("WTF? re-input mf")
                else:
                    value = [valueHorizontal, valueVertical]
                    break
    elif QUESTIONS[PRESENTER_ID]['type'] == "prioritisation":
        selected_choice = input("\nWhich id do you want to prioritize:")
        value = {choice['id']: 0 for choice in PRESENTER_QUESTION['choices']}
        value[selected_choice] = 100
    else:
        choice = input(f"\nЗа какой ID вы хотите проголосовать: ")

    loop = int(input("Сколько голосов вы хотите отправить: "))
    if QUESTIONS[PRESENTER_ID]['type'] in ['wordcloud', 'open']:
        print(f"\nВы выбрали '{choice}' проголосовать '{loop}' раз\n")
    elif QUESTIONS[PRESENTER_ID]['type'] == "qfa":
        print(f"\nВы выбрали '{choice}' проголосовать '{loop}' раз\n")
    elif QUESTIONS[PRESENTER_ID]['type'] == "prioritisation":
        print(f"\nВы выбрали '{selected_choice}' проголосовать '{loop}' раз\n")
    else:
        print(f"\nВы выбрали '{pqi[choice]}' проголосовать '{loop}' раз\n")
    if input("Ты уверен? (Y/N) ").lower() == 'n':
        print("Пока")
        sys.exit(0)
    return choice, TARGET, loop, value, QUESTIONS, PRESENTER_ID, PRESENTER_QUESTION, minutes


# @thread
def main(choice, TARGET, loop, value, QUESTIONS, PRESENTER_ID, PRESENTER_QUESTION, minutes):
    result_available.wait(random.randint(0, minutes*60))
    headers = {
        "origin": "https://menti.com",
        "referer": TARGET,
        "accept": "application/json",
        "content-type": "application/json; charset=UTF-8",
        "user-agent": header.generate()['User-Agent']
    }
    getIdentifier = requests.post("https://www.menti.com/core/identifiers", json={}, headers=headers)
    if getIdentifier.status_code != 200:
        print(f"{getIdentifier.status_code} yo I can't get the Identifier (⊙_⊙)")
        print(getIdentifier.text)
        sys.exit(0)
    headers['x-identifier'] = getIdentifier.json()['identifier']
    DATA = {
        'question_type': QUESTIONS[PRESENTER_ID]['type'],
        'vote': choice
    }
    if QUESTIONS[PRESENTER_ID]['type'] == "ranking":
        DATA['vote'] = [int(choice)]
    if QUESTIONS[PRESENTER_ID]['type'] in ["scales", "prioritisation"]:
        DATA['vote'] = value
    if QUESTIONS[PRESENTER_ID]['type'] == "rating":
        values = {c['id']: [0, 0] for c in PRESENTER_QUESTION['choices']}
        values[int(choice)] = value
        DATA['vote'] = values
    if QUESTIONS[PRESENTER_ID]['type'] == "qfa":
        vote = requests.post(f"https://www.menti.com/core/qfa/{choice}/upvote", headers=headers, json={})
    else:
        vote = requests.post(f"https://www.menti.com/core/votes/{40020414}", headers=headers, json=DATA)
    if vote.status_code not in [201, 200]:
        print(f"{vote.status_code} HAHAHAHAHA LOOKS LIKE ERROR, LOOKS WHAT YOU DID ┐('～`;)┌")
        print(vote.text)
        sys.exit(0)
    global result
    result += 1
    print('Сделано', result)


arg = start()
# arg = *arg
# choice = arg[0]
# TARGET = arg[1]
# loop = arg[2]
# value = arg[3]
# QUESTIONS = arg[4]
# PRESENTER_ID = arg[5]
# PRESENTER_QUESTION = arg[6]
result = 0
result_available = threading.Event()
for i in range(arg[2]):
    thr = threading.Thread(target=main, args=arg)
    # (choice, TARGET, loop, value, QUESTIONS, PRESENTER_ID, PRESENTER_QUESTION))
    thr.start()
