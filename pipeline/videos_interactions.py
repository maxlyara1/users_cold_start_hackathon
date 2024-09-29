import pandas as pd
import streamlit as st
from utils import load_file
import random


def show_ten_videos(df_video, number_videos_from_cat):
    st.markdown(
        "<h3>Выберите видео для подробного просмотра:</h3>", unsafe_allow_html=True
    )

    # Пустой DataFrame для хранения выбранных видео
    ten_videos_df = pd.DataFrame()
    # Проходим по каждой категории и выбираем N наиболее популярных видео
    for _, row in number_videos_from_cat.iterrows():
        # Закомментированный код для случайного выбора группы пользователей
        # if "group" not in st.session_state:
        #     st.session_state.group = random.choice(["A", "B"])
        # if st.session_state.group == "A":
        #     category = random.choice(df_video["category_id"].unique())
        #     N = 1
        # elif st.session_state.group == "B":
        #     category = row["category_id"]
        #     N = row["N"]
        category = random.choice(
            df_video["category_id"].unique()
        )  # Случайный выбор категории
        N = 1  # Количество видео для выбора

        # Фильтруем по категории и сортируем по популярности
        filtered_videos = df_video[df_video["category_id"] == category].sort_values(
            by=["cmments_per_day", "v_long_views_7_days"],
            ascending=(False, False),
        )
        # Выбираем первые N видео
        top_videos = filtered_videos.iloc[:N]
        # Добавляем в итоговый DataFrame
        ten_videos_df = pd.concat([ten_videos_df, top_videos])
    # Сбрасываем индексы для корректного отображения
    ten_videos_df = ten_videos_df.reset_index(drop=True)
    # st.write(ten_videos_df)

    # Отображаем карточки для первых 10 видео
    col1, col2 = st.columns(2)
    for index, row in ten_videos_df.iterrows():
        with col1 if index % 2 == 0 else col2:
            st.markdown(
                f"""
            <div style="background-color: #f5f5f5; border-radius: 10px; padding: 20px; margin-bottom: 20px; width: 100%; height: 150px; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-size: 16px; font-weight: bold; color: #333; text-align: center;">{row['title']} 📽</div>
                <div style="text-align: center; color: #999;">Просмотров: {row['v_year_views']} 👀</div>
                <div style="text-align: center; color: #666;">Дата выхода: {pd.to_datetime(row['v_pub_datetime'], unit='s').strftime('%Y-%m-%d %H:%M')} 📆</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    ten_video_titles = ten_videos_df["title"].tolist()  # Список названий видео
    ten_video_ids = ten_videos_df["video_id"].tolist()  # Список ID видео
    st.session_state.df_video = df_video[
        ~(df_video["video_id"].isin(ten_videos_df["video_id"]))
    ].copy()  # Обновление DataFrame с видео

    with st.form("select_video_form"):
        selected_option = st.selectbox(
            "Выбор видео", options=ten_video_titles, key="video_selectbox"
        )
        selected_video_index = ten_video_titles.index(
            selected_option
        )  # Индекс выбранного видео
        selected_video_id = ten_video_ids[selected_video_index]  # ID выбранного видео
        select_button = st.form_submit_button(label="Просмотр")  # Кнопка для просмотра

        if select_button:
            st.session_state.selected_video = (
                selected_video_id  # Сохранение выбранного видео в session_state
            )
            st.rerun()  # Перезагрузка страницы


def show_video_info(df_video, user_id):
    interactions = []  # Список для хранения взаимодействий
    video_card = None  # Переменная для хранения информации о видео

    if st.session_state.selected_video:
        video_card = df_video[df_video["video_id"] == st.session_state.selected_video]

        if video_card.empty:
            st.session_state.selected_video = (
                None  # Сброс выбранного видео, если оно не найдено
            )
            video_card = None
        else:
            video_card = video_card.iloc[
                0
            ]  # Получение первой строки с информацией о видео

        st.markdown("<hr>", unsafe_allow_html=True)  # Горизонтальная линия
        with st.form(f"Video_{video_card['video_id']}"):
            st.markdown(
                f"""
            <div style="background-color: #f5f5f5; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: #333; margin-bottom: 0;">{video_card['title']} 📽</h3>
                </div>
                <p style="color: #666; margin-bottom: 10px;">{pd.to_datetime(video_card['v_pub_datetime']).strftime('%Y-%m-%d %H:%M')} 📆</p>
                <div style="display: flex; justify-content: space-between; color: #999;">
                    <p>Категория: {video_card['category_id']} 🔖</p>
                    <p>Комментариев: {video_card['v_total_comments']} 💬</p>
                </div>
                <div style="display: flex; justify-content: space-between; color: #999;">
                    <p>Просмотров: {video_card['v_year_views']} 👀</p>
                    <p>Длительность: {round(video_card['v_duration'] / 60, 2)} мин 🕰</p>
                    <p>Лайки: {video_card['v_likes']} 👍</p>
                    <p>Дизлайки: {video_card['v_dislikes']} 👎</p>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            like_dislike = st.selectbox(
                label="Поставьте оценку",
                options=["Нет оценки", "Лайк", "Дизлайк"],
                key=f"like_dislike_{video_card['video_id']}",
            )
            comment = st.checkbox(
                "Оставить комментарий", key=f"comment_{video_card['video_id']}"
            )

            submit_button = st.form_submit_button(label="Отправить")  # Кнопка отправки

            if submit_button:
                if like_dislike == "Лайк":
                    interactions.append((video_card, "like"))  # Добавление лайка
                elif like_dislike == "Дизлайк":
                    interactions.append((video_card, "dislike"))  # Добавление дизлайка
                else:
                    interactions.append(
                        (video_card, "no_like_either_dislike")
                    )  # Без оценки
                if comment:
                    interactions.append(
                        (video_card, "comment")
                    )  # Добавление комментария

                st.session_state.interactions_data = log_user_interaction(
                    interactions, user_id
                )  # Логирование взаимодействий
                st.success(
                    "Ваши взаимодействия сохранены."
                )  # Сообщение об успешном сохранении
                st.session_state.selected_video = None  # Сброс выбранного видео
                st.rerun()  # Перезагрузка страницы для обновления

        # Кнопка "Главное меню" вне формы для немедленного ответа
        if st.button("Главное меню"):
            st.session_state.selected_video = None  # Сброс выбранного видео
            st.rerun()  # Перезагрузка страницы для перехода в главное меню


def log_user_interaction(interactions, user_id):
    try:
        user_interactions_df = load_file(
            path="user_interactions.csv", file_type="csv"
        )  # Загрузка существующих взаимодействий
    except Exception as e:
        st.error(f"Ошибка при загрузке файла: {e}")  # Сообщение об ошибке при загрузке
        user_interactions_df = pd.DataFrame(
            columns=["user_id", "video_id", "category_id", "interaction_type"]
        )  # Создание пустого DataFrame при ошибке

    new_interactions = [
        {
            "user_id": user_id,
            "video_id": video_row["video_id"],
            "category_id": video_row[
                "category_id"
            ],  # Исправлено с "video_id" на "category_id"
            "interaction_type": interaction_type,
        }
        for video_row, interaction_type in interactions
    ]  # Формирование новых взаимодействий

    user_interactions_df = pd.concat(
        [user_interactions_df, pd.DataFrame(new_interactions)], ignore_index=True
    )  # Добавление новых взаимодействий к существующим
    user_interactions_df.to_csv(
        "user_interactions.csv", mode="w", index=False
    )  # Сохранение в CSV

    return user_interactions_df  # Возвращение обновленного DataFrame
