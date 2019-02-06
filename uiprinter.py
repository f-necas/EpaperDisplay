from __future__ import print_function
import requests
import time
import json
import epd

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import datetime

mainFontsize = 24
mainFont = ImageFont.truetype('./font/Lato-Heavy.ttf', mainFontsize)
littleFontsize = 16
littleFont = ImageFont.truetype('./font/Lato-Heavy.ttf', littleFontsize)

with open('credentials.json') as json_data:
    data = json.load(json_data)
    openWeathermapApiKey = data['owmapikey']


# Get day number and add suffix
def getDate(timestamp):
    day = datetime.datetime.fromtimestamp(timestamp).strftime('%d')

    if day == '01':
        suffixe = 'st'
    elif day == '02':
        suffixe = "nd"
    else:
        suffixe = 'th'

    return datetime.datetime.fromtimestamp(timestamp).strftime('%A, %B') + ' ' + day + suffixe


# Convert wind direction in letters
def getWind(windRaw):
    try:
        windDegDirection = windRaw['deg']

        if 11 <= windDegDirection < 79:
            windDir = 'NE'
        elif 79 <= windDegDirection < 124:
            windDir = 'E'
        elif 124 <= windDegDirection < 169:
            windDir = 'SE'
        elif 169 <= windDegDirection < 214:
            windDir = 'S'
        elif 214 <= windDegDirection < 259:
            windDir = 'SW'
        elif 259 <= windDegDirection < 304:
            windDir = 'W'
        elif 304 <= windDegDirection < 349:
            windDir = 'NW'
        else:
            windDir = 'N'
    except:
        windDir = '?'

    wind = str(windRaw['speed'] * 3.6) + ' km/h from ' + windDir

    return wind


# Draw weather icons, texts and wind curve
def drawWeather():
    lineStart = 0
    lineEnd = 0
    City = 'Velaux'
    img = Image.new('RGB', (800, 480), (255, 255, 255))
    d = ImageDraw.Draw(img)

    today = requests.get(
        'http://api.openweathermap.org/data/2.5/weather?q=' + City + '&APPID=' + openWeathermapApiKey).json()

    todayIcon = Image.open('./png/100/' + today['weather'][0]['icon'] + '.jpg').convert('RGB')
    img.paste(todayIcon, (50, 5))

    todayXOffset = 300
    todayYOffset = 10

    d.text((todayXOffset, todayYOffset), City + ' - ' + getDate(today['dt']), fill=(0, 0, 0), font=mainFont)
    d.text((todayXOffset, todayYOffset + 30), today['weather'][0]['main'], fill=(0, 0, 0), font=mainFont)
    d.text((todayXOffset, todayYOffset + 60), getWind(today['wind']), fill=(0, 0, 0), font=mainFont)

    forecast = requests.get(
        'http://api.openweathermap.org/data/2.5/forecast?q=' + City + '&APPID=' + openWeathermapApiKey).json()

    columnOffset = 76
    columnSpaceBetween = 760 / 5

    for data in forecast['list']:
        if datetime.datetime.fromtimestamp(data['dt']).strftime('%H') == '12':
            # print icons and date
            icon = Image.open('./png/45/' + data['weather'][0]['icon'] + '.jpg').convert('RGB')
            img.paste(icon, (columnOffset, 160))
            d.text((columnOffset - 10, 160 + 45), datetime.datetime.fromtimestamp(data['dt']).strftime('%d/%m'),
                   fill=(0, 0, 0), font=mainFont)

            # print wind speed and draw line
            windkmh = data['wind']['speed'] * 3.6
            windheight = 400 - windkmh
            d.text((columnOffset + 5, windheight - 30), '%.2f' % windkmh + '', fill=(0, 0, 0), font=littleFont)
            lineEnd = (columnOffset + 20, windheight)
            if lineStart:
                d.line([lineStart, lineEnd], fill=(0, 0, 0), width=3)
            columnOffset += columnSpaceBetween
            lineStart = lineEnd
        # https://openweathermap.org/weather-conditions

    img.save('ui.png')

    return img


# Assembling all images
def drawImage():
    img = Image.new('RGB', (480, 800), (255, 255, 255))

    weather = drawWeather().rotate(90, expand=1)
    img.paste(weather, (0, 0))

    img.save('uidone.png')

    # then = time.time()
    epd.update_screen(img)

    # now = time.time()  # Time after it finished

    # print('Global: ', now - then, ' seconds')




