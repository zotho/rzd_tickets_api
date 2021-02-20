import logging

import requests
import time
from datetime import datetime

logger = logging.getLogger(__name__)


def get_rid():
    url = "https://pass.rzd.ru/timetable/public/?layer_id=5827&dir=0&code0=2030000&code1=2030284&tfl=3&checkSeats=1&dt0=06.03.2021"

    headers = {
      "Cookie": "AuthFlag=false; ClientUid=5d23KLnjYHWdwM0O4FVz2JujGtavmFNJ; lang=ru; JSESSIONID=0000qij7a0PG6gRBz2orc-QkqtU:17obqb0dk"
    }

    rest = 5
    while rest > 0:
        rest -= 1
        logger.debug(rest)
        try:
            response = requests.request("GET", url, headers=headers, timeout=3)
        except requests.exceptions.ConnectTimeout:
            if rest <= 0:
                return None
        else:
            break

    logger.debug(response.text)

    RID = response.json()["RID"]
    CUid = response.cookies["ClientUid"]
    JSid = response.cookies["JSESSIONID"]
    return RID, JSid, CUid


def get_data(RID, JSid, CUid):
    url = "https://pass.rzd.ru/timetable/public/ru?layer_id=5827"
    payload=f"rid={RID}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"AuthFlag=false; ClientUid={CUid}; lang=ru; JSESSIONID={JSid}"
    }

    response = {}
    rest = 5
    while response.get("result") != "OK" and rest > 0:
        rest -= 1
        logger.debug(rest)
        try:
            response = requests.request("POST", url, headers=headers, data=payload, timeout=2).json()
        except requests.exceptions.ConnectTimeout:
            if rest <= 0:
                return None

    logger.debug(response)

    return response


def call_api():
    RID = get_rid()
    if not RID:
        return None

    time.sleep(1)
    data = get_data(*RID)
    if not data:
        return None

    train = next(filter(lambda train: train["number"] == "012Я", data["tp"][0]["list"]))
    car = next(filter(lambda car: car["typeLoc"] == "СВ", train["cars"]))
    tariff = car["tariff"]
    free = car["freeSeats"]
    timestamp = datetime.strptime(data["timestamp"], "%d.%m.%Y %H:%M:%S.%f")
    return car, tariff, free, timestamp


if __name__ == "__main__":
    call_api()
