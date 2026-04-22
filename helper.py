import st
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
from streamlit import cache_data
import emoji
extract = URLExtract()
@cache_data
def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # total messages
    num_messages = df.shape[0]

    # total words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # total media
    num_media = df[df['message'] == '<Media omitted>\n'].shape[0]

    # All links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

# Word Cloud
from wordcloud import WordCloud
@cache_data
def create_wordcloud(selected_user, df):

    with open("stop_hinglish.txt", "r", encoding="utf-8") as f:
        stop_words = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('Media omitted', na=False)]

    def remove_stopwords(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    temp['message'] = temp['message'].apply(remove_stopwords)

    wc = WordCloud(
        width=900,
        height=450,
        min_font_size=10,
        background_color='white'
    )

    df_wc = wc.generate(temp['message'].str.cat(sep=" "))

    return df_wc

# common words
def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

# emojis
@cache_data
def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

# Monthly Timeline
@cache_data
def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

#Daily Timeline
@cache_data
def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline
@cache_data
def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()
@cache_data
def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()
@cache_data
def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap

def peak_hour(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return int(df['hour'].mode()[0])

def avg_messages_per_day(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return round(df.groupby('only_date').size().mean(), 2)

def smart_summary(selected_user, df):

    total = fetch_stats(selected_user, df)[0]
    peak = peak_hour(selected_user, df)
    avg = avg_messages_per_day(selected_user, df)

    return f"""
    Total messages sent: {total}

    Peak chat hour: {peak}:00

    Average messages/day: {avg}
    """


