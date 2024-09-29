import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


@st.cache_data
def get_initial_info(df_logs_5, df_video):
    """
    Получает начальную информацию, объединяя логи и данные о видео.

    Args:
        df_logs_5 (pd.DataFrame): DataFrame с логами просмотров видео.
        df_video (pd.DataFrame): DataFrame с данными о видео.

    Returns:
        tuple: DataFrame с рангами категорий и агрегированными рангами.
    """
    # Объединение данных по video_id
    df_merged = pd.merge(
        df_logs_5[["video_id", "region", "watchtime"]],
        df_video[["video_id", "category_id"]],
        on="video_id",
        how="inner",
    )

    # Вычисление среднего watchtime для каждой категории по каждому региону
    df_avg_watchtime = df_merged.groupby(["region", "category_id"], as_index=False).agg(
        avg_watchtime=("watchtime", "mean")
    )

    # Определение топ-10 категорий по каждому региону
    df_avg_watchtime["rank"] = df_avg_watchtime.groupby("region")["avg_watchtime"].rank(
        method="first", ascending=False
    )

    # Найдём средний ранг для каждой категории
    df_ranks_grouped = (
        df_avg_watchtime.groupby("category_id")
        .agg(avg_rank=("rank", "mean"))
        .reset_index()
    )

    df_ranks_grouped = df_ranks_grouped[
        df_ranks_grouped["avg_rank"] <= 10
    ]  # Фильтруем только топ-10 категорий

    df_ranks = df_avg_watchtime[
        df_avg_watchtime["category_id"].isin(df_ranks_grouped["category_id"].unique())
    ]

    return (
        df_ranks,
        df_ranks_grouped,
    )  # Возвращаем DataFrame с рангами категорий и агрегированными рангами


@st.cache_data
def create_plot(df_ranks, df_ranks_grouped):
    """
    Создает график распределения рангов категорий.

    Args:
        df_ranks (pd.DataFrame): DataFrame с рангами категорий.
        df_ranks_grouped (pd.DataFrame): DataFrame с агрегированными рангами категорий.

    Returns:
        plotly.graph_objects.Figure: График распределения рангов.
    """
    df_ranks_grouped = df_ranks_grouped.sort_values(
        by="avg_rank"
    )  # Сортируем по среднему рангу
    category_order = df_ranks_grouped[
        "category_id"
    ].tolist()  # Получаем порядок категорий

    # Создаем боксовую диаграмму
    fig = px.box(
        df_ranks,
        x="category_id",
        y="rank",
        category_orders={"category_id": category_order},
    )

    # Добавляем средний ранг каждой категории
    for index, row in df_ranks_grouped.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["category_id"]],
                y=[row["avg_rank"]],
                mode="markers",
                marker=dict(color="red", size=12),
                showlegend=False,
            )
        )

    fig.update_layout(
        title="Распределение рангов категорий среди всех регионов",
        xaxis_title="",
        yaxis_title="Rank",
        xaxis=dict(tickangle=0),
        showlegend=True,
    )

    # Настройка шрифта подписей на осях
    fig.update_xaxes(tickfont=dict(size=18))  # Увеличение шрифта подписей на оси X
    fig.update_yaxes(tickfont=dict(size=18))

    return fig  # Возвращаем созданный график
