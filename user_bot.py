from pyrogram import Client, filters
import pyrogram, datetime, pprint
import requests


# Your telegram api client.
# Get api_id and api_hash here: https://my.telegram.org/
app = Client(
    "my_telegram_userbot",
    api_id="your api id",
    api_hash="your api hash"
)


# Secondary (tool) function.
async def _title_normalize(title):
    title = title.replace(
        "January", "Январь"
    ).replace(
        "February", "Февраль"
    ).replace(
        "March", "Март"
    ).replace(
        "April", "Апрель"
    ).replace(
        "May", "Май"
    ).replace(
        "June", "Июнь"
    ).replace(
        "July", "Июль"
    ).replace(
        "August", "Август"
    ).replace(
        "September", "Сентябрь"
    ).replace(
        "October", "Октябрь"
    ).replace(
        "November", "Ноябрь"
    ).replace(
        "December", "Декабрь"
    )

    return title


# Main function!
async def get_all_podcasts():
    # Just a new list object.
    new_data = []

    async for message in app.get_chat_history("@ikniga"):
        # If message has a caption, then it's a podcast.
        # If message has a text, then it's a descriptions of a podcast.
        text = message.text if not message.text else message.text

        # date in string
        _datetime = str(message.date)

        # get year and reformat to int
        _year = int(_datetime.split(" ")[0].split("-")[0])
        
        # get month and reformat to int
        _month = int(_datetime.split(" ")[0].split("-")[1])
        
        # get day and reformat to int
        _day = int(_datetime.split(" ")[0].split("-")[2])

        # There is "Слушай, становись умнее и успешнее" in podcast's caption.
        # There is "Книга #<int>" in description's text.
        if "Слушай, становись умнее и успешнее" in str(text) or "Книга #" in str(text):
            # text if message is description
            text = 'Пусто' if message.text is None else message.text
            
            # caption if message is podcast
            caption = "Пусто" if message.caption is None else message.caption

            # On start list of messages(podcast + description) is empty
            if len(new_data) == 0:
                # Create new object with None properties. 
                # We will change every None to some message data soon.
                new_data.append({"podcast": None, "description": None})

            # Reformat the date
            _date = str(
                    datetime.datetime(year=_year, month=_month, day=_day).strftime(
                        "%d %B %Y"
                    )
                )  # .replace(".", "")
            
            # Normalize date (translate month to russian lang)
            _date = await _title_normalize(_date)

            # If caption is not empty, then it is podcast
            if caption != "Пусто" and new_data[new_data.__len__() - 1]['podcast'] is None:
                # Add Podcast to list
                new_data[-1]['podcast'] = {"id": message.id, "type": "podcast", "text": text, "caption": caption, "date": _date, "url": message.link}
                
                # If you want to debug
                # print("Added podcast:", message.link, "Data:", new_data[-1])

            # If text is not empty, then it is description
            if text != "Пусто" and new_data[new_data.__len__() - 1]['description'] is None:
                # Add Description to list
                new_data[-1]['description'] = {"id": message.id, "type": "description", "text": text, "caption": caption, "date": _date, "url": message.link}
                
                # If you want to debug
                # print("Added description:", message.link, "Data:", new_data[-1])

            # If last element in list is fully empty (if both podcast and description are None).
            if new_data[-1]['podcast'] is not None and new_data[-1]['description'] is not None:
                # Append new empty scheme element, because the last element of list is already fully filled.
                new_data.append({"podcast": None, "description": None})
                
                # If you want to debug
                # print("Appended new scheme cuz last data is full")

    # Remove last element, because the first post of channel is system message about creation of channel.
    # ЭТО НУЖНО! Не удаляй.
    new_data.pop()

    # return new_data list.
    return new_data


# We don't need this. This is for pure fun and debug(sometimes).
# Это мусор, но пусть стоит.
async def print_all_podcasts():
    new_data = []

    async for message in app.get_chat_history("@ikniga"):
        if message.voice and message.caption or message.audio and message.caption:
            # _splitted_title = str(message.audio.title).split("_")[0] if message.audio else str(message.date)
            # _splitted_title = str(_splitted_title)
            # print("_splitted_title:", _splitted_title[0:2])

            _datetime = str(message.date)
            _year = int(_datetime.split(" ")[0].split("-")[0])
            _month = int(_datetime.split(" ")[0].split("-")[1])
            _day = int(_datetime.split(" ")[0].split("-")[2])

            _title = (
                str(
                    datetime.datetime(year=_year, month=_month, day=_day).strftime(
                        "%d %B %Y"
                    )
                )
                if message.voice
                else str(
                    datetime.datetime(year=_year, month=_month, day=_day).strftime(
                        "%d %B %Y"
                    )
                )
                if message.audio.title.split("_")[0].isdigit()
                else message.audio.title
            )
            _title = str(_title)
            _title = await _title_normalize(_title)

            _message_id = str(message.id)

            _message_link = str(message.link)

            _date = message.date
            _date = str(_date)

            _duration_seconds = (
                message.voice.duration if message.voice else message.audio.duration
            )
            _duration_seconds = str(_duration_seconds)

            _duration_minutes = int(_duration_seconds) / 60
            _duration_minutes = (
                str(_duration_minutes).split(".")[0]
                + "."
                + str(_duration_minutes).split(".")[1][0:1]
            )

            _type = (
                "voice"
                if message.voice
                else "audio"
                if message.audio.title
                else "unknown"
            )
            _type = str(_type)

            _file_name = (
                f"{_date}.{message.voice.mime_type.split('/')[1]}"
                if message.voice
                else f"{_title}-{message.audio.file_name}"
            )
            _file_name = (
                str(_file_name).replace("..", ".").replace("--", "").replace("-.", ".")
            )

            print(
                "Title:",
                _title + "\nType:",
                _type,
                "\nFile name:",
                _file_name,
                "\nDate:",
                _date,
                "\nDuration (sec.):",
                _duration_seconds,
                "\nDuration (min.):",
                _duration_minutes,
                "\nMessage ID:",
                _message_id,
                "\nMessage link:",
                _message_link,
                end="\n\n",
            )


@app.on_message(filters.chat("@skibidibub"))
async def hello(client: pyrogram.Client, message: pyrogram.types.Message):
    data = await get_all_podcasts()

    #Убери комменты/хештеги, если хочешь вывести данные/ссылки красиво.
    for obj in data:
              print("~~~~~~~~~\n" + 
              f"{obj['podcast']['id']}. Podcast: {obj['podcast']['url']}\n" +
              f"{obj['description']['id']}. Description: {obj['description']['url']}\n" + 
              "~~~~~~~~~", 
              end="\n\n")

app.run()
