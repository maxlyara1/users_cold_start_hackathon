@st.cache_data
def recommend_categories(df_ranks_grouped, interactions_data, total_representatives=10):
    """
    Рекомендует категории на основе взаимодействий пользователя.

    Args:
        df_ranks_grouped (pd.DataFrame): DataFrame с агрегированными рангами категорий.
        interactions_data (pd.DataFrame): DataFrame с данными взаимодействий пользователя.
        total_representatives (int): Общее количество рекомендованных видео.

    Returns:
        pd.DataFrame: DataFrame с категориями, количеством видео и процентами.
    """
    df = df_ranks_grouped.copy()  # Создаем копию DataFrame для обработки

    # Проверка наличия колонки 'N' в df, если её нет, инициализируем её
    if "N" not in df.columns:
        df["N"] = 0  # Инициализация, если не существует

    # Создаем словарь весов категорий на основе текущего количества видео
    category_weights = {row["category_id"]: row["N"] for _, row in df.iterrows()}

    # Обрабатываем каждое взаимодействие пользователя
    for _, interaction in interactions_data.iterrows():
        category_id = interaction["category_id"]  # ID категории
        interaction_type = interaction["interaction_type"]  # Тип взаимодействия

        if category_id in category_weights:
            if interaction_type == "like":
                category_weights[category_id] += 1  # Увеличиваем вес при лайке
            elif interaction_type == "dislike":
                category_weights[category_id] -= 1  # Уменьшаем вес при дизлайке
            elif interaction_type == "comment":
                category_weights[category_id] += 2  # Увеличиваем вес при комментарии
            elif interaction_type == "no_like_either_dislike":
                category_weights[category_id] -= 0.5  # Немного уменьшаем вес без оценки

    total_weight = sum(category_weights.values())  # Общий вес всех категорий

    if total_weight <= 0:
        raise ValueError(
            "Все веса категорий стали отрицательными или равны нулю."
        )  # Проверка на валидность весов

    # Обновляем количество видео 'N' на основе новых весов
    df["N"] = df["category_id"].map(category_weights).fillna(0)  # Заполняем NaN нулями
    df["N"] = (df["N"] / total_weight * total_representatives).round().astype(int)

    # Балансировка общего количества видео до total_representatives
    while df["N"].sum() != total_representatives:
        diff = (
            total_representatives - df["N"].sum()
        )  # Разница между желаемым и текущим количеством видео
        if diff > 0:
            idx = df[
                "N"
            ].idxmax()  # Находим индекс категории с наибольшим количеством видео
            df.at[idx, "N"] += 1  # Увеличиваем количество видео в этой категории
        else:
            idx = df[
                "N"
            ].idxmin()  # Находим индекс категории с наименьшим количеством видео
            if df.at[idx, "N"] > 0:
                df.at[
                    idx, "N"
                ] -= 1  # Уменьшаем количество видео в этой категории, если возможно

    # Рассчитываем проценты для каждой категории
    df["Percentage"] = (df["N"] / total_representatives * 100).round(2)

    # Формируем итоговый DataFrame с необходимыми колонками
    df_ranks_grouped_N = (
        df[["category_id", "N", "Percentage"]]
        .sort_values(by="N", ascending=False)
        .reset_index(drop=True)
        .copy()
    )

    return df_ranks_grouped_N  # Возвращаем итоговый DataFrame
