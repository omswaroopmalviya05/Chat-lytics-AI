import re
import pandas as pd
import streamlit as st

@st.cache_data
def preprocessor(data):
    pattern = r'^\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s-\s'

    dates = re.findall(pattern, data, flags=re.MULTILINE)
    messages = re.split(pattern, data, flags=re.MULTILINE)

    df = pd.DataFrame({
        'message_date': dates,
        'user_message': messages[1:]
    })

    df['message_date'] = pd.to_datetime(df['message_date'],
                                        format='%d/%m/%y, %H:%M - ')

    df.rename(columns={'message_date': 'date'}, inplace=True)


    users = []
    messages_clean = []

    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)

        if entry[1:]:
            users.append(entry[1])
            messages_clean.append(entry[2])
        else:
            users.append('group_notification')
            messages_clean.append(entry[0])

    df['user'] = users
    df['message'] = messages_clean
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df

