import streamlit as st
import pandas as pd


@st.cache_data
def load_file(path, file_type="parquet"):
    """
    Загружает файл в зависимости от его типа.

    Args:
        path (str): Путь к файлу.
        file_type (str): Тип файла ("parquet" или "csv").

    Returns:
        pd.DataFrame: Загруженный DataFrame.
    """
    if file_type == "parquet":
        df = pd.read_parquet(path)  # Загружаем данные из файла Parquet
    elif file_type == "csv":
        df = pd.read_csv(path)  # Загружаем данные из файла CSV
    return df  # Возвращаем загруженный DataFrame


def get_current_time_specific_info():
    """
    Получает информацию о самых популярных категориях в текущее время суток.
    """
    # Здесь должна быть ваша реализация получения информации о популярных категориях
    pass  # Заглушка для будущей реализации


def create_embeddings_and_clusters():
    """
    Создает эмбеддинги и кластеры для подкатегорий.
    """
    # Здесь должна быть ваша реализация создания эмбеддингов и кластеров
    pass  # Заглушка для будущей реализации
