import streamlit as st
from utils import load_file
from data_processing import (
    get_initial_info,  # Функция для получения начальной информации
    create_plot,  # Функция для создания графика
)
from videos_interactions import (
    show_ten_videos,
    show_video_info,
)  # Функции для работы с видео
from recommendation_engine import (
    first_recommend_categories,  # Рекомендации категорий при первом запуске
    recommend_categories,  # Рекомендации категорий на основе взаимодействий
    recommend_subcategories,  # Рекомендации подкатегорий
)
import pandas as pd
from datetime import datetime
import uuid
import numpy as np
import plotly.express as px  # Добавляем plotly для визуализации


# Функция для отображения страницы пользователя
def display_page(df_logs_5, df_video, user_id):
    # Кнопка "Обновить страницу" в боковой панели
    page_relaunch_button = st.sidebar.button(
        "Обновить страницу", key=f"update_page_{datetime.now()}"
    )

    if page_relaunch_button:
        st.session_state.first_launch = (
            True  # Если нажата кнопка, сбрасываем флаг первого запуска
        )
        st.rerun()  # Перезагружаем страницу

    # Инициализация 'first_launch' в session_state
    if "first_launch" not in st.session_state:
        st.session_state.first_launch = True  # Устанавливаем флаг первого запуска

    df_ranks, df_ranks_grouped = get_initial_info(
        df_logs_5, df_video
    )  # Получаем ранги категорий

    # Если это первый запуск или нажата кнопка обновления страницы
    if st.session_state.first_launch:
        # Создание графика
        fig = create_plot(df_ranks, df_ranks_grouped)
        # Интерфейс Streamlit
        with st.expander(
            "Распределение рангов категорий среди всех регионов", expanded=False
        ):
            st.plotly_chart(fig)  # Отображаем график
        st.session_state.first_launch = False  # Сбрасываем флаг после первого запуска

    # Проверка условия для вывода рекомендаций
    if st.session_state.first_launch:
        number_videos_from_cat = first_recommend_categories(
            df_ranks_grouped
        )  # Первая рекомендация категорий
    else:
        number_videos_from_cat = recommend_categories(
            df_ranks_grouped, st.session_state.interactions_data
        )  # Рекомендации на основе взаимодействий

    # Визуализация вероятностей категорий в процентах
    with st.expander("Вероятности категорий в процентах", expanded=True):
        total_videos = number_videos_from_cat[
            "N"
        ].sum()  # Рассчитываем общую сумму N для расчета процентов
        df_percentage = number_videos_from_cat.copy()
        df_percentage["Percentage"] = (df_percentage["N"] / total_videos * 100).round(
            2
        )  # Добавляем колонку процентов

        # Создаем график
        fig_percentage = px.pie(
            df_percentage,
            names="category_id",  # Категории для отображения
            values="Percentage",  # Процентное значение
            title="Распределение вероятностей категорий",
            hole=0.3,  # Визуализация с кругом по центру
        )
        st.plotly_chart(fig_percentage)  # Отображаем график

    # Инициализация 'selected_video' в session_state, если отсутствует
    if "selected_video" not in st.session_state:
        st.session_state.selected_video = None
    if st.session_state.selected_video is None:
        show_ten_videos(
            st.session_state.df_video, number_videos_from_cat
        )  # Показать 10 видео

    # Отображаем информацию о видео, с которым пользователь взаимодействует
    if st.session_state.selected_video:
        show_video_info(df_video, user_id)


# Основная функция Streamlit
def main():
    st.title("Демонстрация работы алгоритма холодного старта")  # Заголовок
    st.subheader("Команда ikanam_chipi_chipi")  # Подзаголовок
    loading_message = st.warning(
        "Первый запуск может занять некоторое время. Пожалуйста, подождите..."
    )  # Сообщение о загрузке

    # Загрузка логов
    df_logs_5 = load_file("data/sample.parquet", file_type="parquet")
    # Загрузка информации о видео
    df_video = load_file("data/video_stat.parquet", file_type="parquet")
    if "df_video" not in st.session_state:
        st.session_state.df_video = (
            df_video  # Сохранение информации о видео в session_state
        )

    loading_message.empty()  # Удаление сообщения о загрузке

    # Генерация уникального user_id и сохранение в session_state
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(
            uuid.uuid4()
        )  # Генерация уникального ID пользователя

    user_id = st.session_state.user_id  # Получение ID пользователя

    # Отображаем страницу пользователя
    display_page(df_logs_5, df_video, user_id)


if __name__ == "__main__":
    main()  # Запуск основного приложения
