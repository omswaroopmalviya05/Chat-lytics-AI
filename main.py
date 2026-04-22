import streamlit as st
import helper
import plotly.express as px
import plotly.graph_objects as go
from preprocessor import preprocessor

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="Chat-lytics AI",
    layout="wide"
)

# ---------------------------------
# HEADER
# ---------------------------------
st.title("Chat-lytics AI")
st.caption("Conversation Analytics Platform")
# ---------------------------------
# SIDEBAR
# ---------------------------------
st.sidebar.title("Chat Analyzer")

uploaded_file = st.sidebar.file_uploader(
    "Upload Chat (.txt)",
    type=["txt"]
)

# ---------------------------------
# MAIN APP
# ---------------------------------
if uploaded_file is not None:

    data = uploaded_file.getvalue().decode("utf-8")

    st.success("File uploaded successfully!")

    df = preprocessor(data)

    st.success("Chat analyzed successfully!")

    # -------------------------------
    # USER LIST
    # -------------------------------
    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    st.sidebar.subheader("Show Analysis W.R.T.")
    selected_user = st.sidebar.selectbox(
        "Select User",
        user_list
    )

    run = st.sidebar.button("Start Analysis")

    # ---------------------------------
    # ANALYSIS START
    # ---------------------------------
    if run:

        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Overview", "📈 Trends", "👥 Users", "🧠 Insights"]
        )

        # =====================================
        # TAB 1 : OVERVIEW
        # =====================================
        with tab1:

            st.header("📊 Overview")

            num_messages, words, num_media, links = helper.fetch_stats(
                selected_user, df
            )

            peak = helper.peak_hour(selected_user, df)

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Messages", num_messages)
            col2.metric("Words", words)
            col3.metric("Media", num_media)
            col4.metric("Links", links)
            col5.metric("Peak Hour", f"{peak}:00")

        # =====================================
        # TAB 2 : TRENDS
        # =====================================
        with tab2:

            st.header("📈 Trends")

            # Monthly Timeline
            st.subheader("Monthly Timeline")

            timeline = helper.monthly_timeline(selected_user, df)

            fig = px.line(
                timeline,
                x="time",
                y="message",
                markers=True
            )

            fig.update_layout(height=450)

            st.plotly_chart(fig, use_container_width=True)

            # Daily Timeline
            st.subheader("Daily Timeline")

            daily = helper.daily_timeline(selected_user, df)

            fig = px.line(
                daily,
                x="only_date",
                y="message",
                markers=True
            )

            fig.update_layout(height=450)

            st.plotly_chart(fig, use_container_width=True)

            # Activity Map
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Most Busy Day")

                busy_day = helper.week_activity_map(selected_user, df)

                fig = px.bar(
                    x=busy_day.index,
                    y=busy_day.values
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Most Busy Month")

                busy_month = helper.month_activity_map(
                    selected_user, df
                )

                fig = px.bar(
                    x=busy_month.index,
                    y=busy_month.values
                )

                st.plotly_chart(fig, use_container_width=True)

            # Heatmap
            st.subheader("Weekly Activity Heatmap")

            heatmap = helper.activity_heatmap(selected_user, df)

            fig = go.Figure(
                data=go.Heatmap(
                    z=heatmap.values,
                    x=list(heatmap.columns.astype(str)),
                    y=list(heatmap.index.astype(str)),
                    colorscale="Blues",
                    hoverongaps=False
                )
            )

            fig.update_layout(
                height=500,
                xaxis_title="Hour Range",
                yaxis_title="Day",
                xaxis_type="category"
            )

            st.plotly_chart(fig, use_container_width=True)
        # =====================================
        # TAB 3 : USERS
        # =====================================
        with tab3:

            st.header("👥 User Analysis")

            if selected_user == "Overall":

                x, new_df = helper.most_busy_users(df)

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Most Busy Users")

                    fig = px.bar(
                        x=x.index,
                        y=x.values
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                with col2:
                    st.subheader("Contribution %")
                    st.dataframe(new_df)

            # WordCloud
            st.subheader("WordCloud")

            wc = helper.create_wordcloud(
                selected_user, df
            )

            st.image(wc.to_array())

            # Common Words
            st.subheader("Most Common Words")

            common_df = helper.most_common_words(
                selected_user, df
            )

            fig = px.bar(
                common_df,
                x=1,
                y=0,
                orientation="h"
            )

            st.plotly_chart(fig, use_container_width=True)

            # Emoji
            st.subheader("Emoji Analysis")

            emoji_df = helper.emoji_helper(
                selected_user, df
            )

            if not emoji_df.empty:

                col1, col2 = st.columns(2)

                with col1:
                    st.dataframe(emoji_df)

                with col2:
                    fig = px.pie(
                        emoji_df.head(),
                        values=1,
                        names=0
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

        # =====================================
        # TAB 4 : INSIGHTS
        # =====================================
        with tab4:

            st.header("🧠 Smart Insights")

            summary = helper.smart_summary(
                selected_user, df
            )

            st.success(summary)

            avg = helper.avg_messages_per_day(
                selected_user, df
            )

            st.metric(
                "Average Messages / Day",
                round(avg, 2)
            )

            # Download CSV
            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇ Download Cleaned Data",
                csv,
                "whatsapp_chat.csv",
                "text/csv"
            )