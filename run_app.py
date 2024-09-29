import os

# Убедитесь, что переменная окружения STREAMLIT_APP задана правильно
os.environ["STREAMLIT_APP"] = "pipeline/app.py"

# Запуск приложения Streamlit
os.system("streamlit run pipeline/app.py")
