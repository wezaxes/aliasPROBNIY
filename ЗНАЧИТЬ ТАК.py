# ===============================
# ІМПОРТИ БІБЛІОТЕК
# ===============================

import streamlit as st          # Основна бібліотека для веб-інтерфейсу
import random                  # Для рандому (слова, коди, перемішування)
import time                    # Для таймерів / затримок (може знадобитись далі)
import os                      # Робота з файлами та файловою системою
import json                    # Для парсингу JSON (ключі доступу)
import string                  # Набір букв і цифр (для генерації коду кімнати)
from google.cloud import firestore             # Firestore (база даних)
from google.oauth2 import service_account      # Авторизація Google сервісів


# ===============================
# 1. НАЛАШТУВАННЯ СТОРІНКИ
# ===============================

# Встановлює базові параметри сторінки Streamlit
st.set_page_config(
    page_title="Alias Ultimate - Wezaxes Edition",  # Назва вкладки браузера
    page_icon="🎮",                                 # Іконка вкладки
    layout="centered"                               # Центрований layout
)


# ===============================
# 2. СТИЛІЗАЦІЯ (CSS)
# ===============================

# Вставка кастомного CSS для всього інтерфейсу
st.markdown("""
    <style>

    /* Центруємо кнопки Streamlit */
    .stButton { display: flex; justify-content: center; }

    /* Стиль самих кнопок */
    .stButton>button { 
        width: 100%;                 /* Кнопка на всю ширину */
        height: 4.5em;               /* Висота кнопки */
        font-size: 24px !important;  /* Великий текст */
        font-weight: bold; 
        border-radius: 15px; 
        margin-bottom: 10px; 
        text-transform: uppercase;   /* Всі літери великі */
    }

    /* Центрування всіх заголовків і тексту */
    h1, h2, h3, p { text-align: center !important; }

    /* Блок зі словом (у грі) */
    .word-box { 
        font-size: 42px; 
        text-align: center; 
        font-weight: bold; 
        color: #f9e2af; 
        background-color: #313244; 
        padding: 50px; 
        border-radius: 20px; 
        border: 3px solid #89b4fa; 
        margin: 20px 0; 
    }

    /* Блок дисклеймера */
    .disclaimer-box {
        text-align: center; 
        background-color: #45475a; 
        padding: 25px; 
        border-radius: 15px; 
        border: 2px solid #f38ba8;
    }

    /* Екран очікування / лобі */
    .waiting-screen {
        background-color: #1e1e2e; 
        padding: 50px; 
        border-radius: 25px;
        border: 3px dashed #fab387; 
        color: #fab387; 
        text-align: center;
    }

    /* Попереджувальний текст */
    .warning-text {
        color: #f38ba8; 
        font-weight: bold; 
        font-size: 28px; 
        border: 2px solid #f38ba8; 
        padding: 10px; 
        border-radius: 10px;
        margin-top: 20px; 
        text-transform: uppercase;
    }

    /* ---------------------------
       ДИЗАЙН ПЛИТОК РЕЖИМІВ
       --------------------------- */

    .mode-selection {
        padding: 30px; 
        border-radius: 20px; 
        background: #cdd6f4;         /* Світлий фон */
        border: 3px solid #89b4fa; 
        margin-bottom: 20px;
        transition: 0.3s;            /* Анімація ховера */
        cursor: pointer;
        display: block;
        width: 100%;
        text-decoration: none !important;
        color: #000000 !important;   /* Примусово чорний текст */
    }

    /* Ефект наведення */
    .mode-selection:hover {
        background: #bac2de;
        border-color: #fab387;
        transform: scale(1.02);
    }

    /* Примусово чорний текст всередині плиток */
    .mode-selection h3, 
    .mode-selection p, 
    .mode-selection span { 
        color: #000000 !important; 
        margin-top: 0; 
        text-decoration: none !important;
    }

    /* Щоб посилання не міняли колір */
    a:link, a:visited, a:hover, a:active {
        text-decoration: none !important;
        color: inherit !important;
    }

    /* Кнопка фідбеку */
    .feedback-btn {
        background-color: #38bdf8 !important;
        border: none !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)


# Додатковий CSS для коректної ширини контейнерів
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div.stElementContainer {
        width: 100%;
        margin-bottom: 10px;
    }

    div.stButton {
        width: 100%;
        display: flex;  
        justify-content: center;
    }

    div.stButton > button {
        width: 100%;
    }      
    </style>
""", unsafe_allow_html=True)


# ===============================
# ДОПОМІЖНІ ФУНКЦІЇ
# ===============================

def generate_room_code():
    # Генеруємо 4 великі літери
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))

    # Генеруємо 2 цифри
    digits = ''.join(random.choices(string.digits, k=2))

    # Об'єднуємо літери й цифри в список
    code_list = list(letters + digits)

    # Перемішуємо символи
    random.shuffle(code_list)

    # Повертаємо код як рядок
    return ''.join(code_list)


# Кешуємо підключення до бази, щоб не створювалось щоразу
@st.cache_resource
def get_db():
    try:
        # Беремо JSON-ключ із secrets
        key_dict = json.loads(st.secrets["textkey"])

        # Створюємо креденшали
        creds = service_account.Credentials.from_service_account_info(key_dict)

        # Повертаємо клієнт Firestore
        return firestore.Client(credentials=creds)
    except:
        # Якщо щось пішло не так — просто None
        return None


# Підключення до бази
db = get_db()


def load_words():
    filename = "words.txt"

    # Перевіряємо, чи існує файл
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            # Зчитуємо всі непорожні рядки
            words = [line.strip() for line in f if line.strip()]

            # Якщо слова є — повертаємо їх
            if words:
                return words

    # Якщо файлу немає або він пустий — дефолтний список
    return [
        "Пудж", "Бебра", "Стан", "Мід", "Рошан",
        "Сленг", "Крінж", "Абобус", "Wezaxes", "Тільт"
    ]


def append_word_to_file(word):
    try:
        # Додаємо слово в кінець файлу
        with open("words.txt", "a", encoding="utf-8") as f:
            f.write(word + "\n")
    except:
        # Якщо не вдалось — мовчки ігноруємо
        pass


# ===============================
# ІНІЦІАЛІЗАЦІЯ SESSION STATE
# ===============================

# Усі слова гри
if 'all_words' not in st.session_state:
    st.session_state.all_words = load_words()

# Дані для повідомлень (текст + тип)
if 'msg_data' not in st.session_state:
    st.session_state.msg_data = {"text": None, "type": None}

# Останнє додане слово
if 'last_added_word' not in st.session_state:
    st.session_state.last_added_word = ""

# Основні стани гри
if 'game_state' not in st.session_state:
    st.session_state.game_state = "welcome"      # Поточний екран
    st.session_state.game_mode = None            # irl / discord
    st.session_state.players = []                # Список гравців
    st.session_state.scores = {}                 # Очки гравців
    st.session_state.current_player_idx = 0      # Хто зараз ходить
    st.session_state.current_round = 1           # Номер раунду


# ===============================
# САЙДБАР
# ===============================

with st.sidebar:
    st.markdown("---")
    st.markdown("### 💡 Маєш ідею або щось зламалось?")
    st.link_button(
        "ЗАПРОПОНУВАТИ ФІЧУ/НАЯБІДНІЧАТЬ ✈️",
        "https://t.me/aliashihibot",
        use_container_width=True
    )
    st.markdown("---")


# ===============================
# ОБРОБКА URL-ПАРАМЕТРІВ
# ===============================

# Отримуємо query-параметри з URL
params = st.query_params

# Якщо передано режим гри
if "mode" in params:
    st.session_state.game_mode = params["mode"]   # Зберігаємо режим
    st.session_state.game_state = "setup"         # Переходимо до сетапу
    st.query_params.clear()                       # Чистимо URL
    st.rerun()                                    # Перезапуск додатку
# ===============================
# ЕКРАНИ ГРИ (STATE MACHINE)
# ===============================
# Тут починається логіка перемикання екранів.
# Все керується через st.session_state.game_state


# -------------------------------------------------
# WELCOME / ДИСКЛЕЙМЕР
# -------------------------------------------------
if st.session_state.game_state == "welcome":

    # Заголовок сторінки (HTML, щоб задати колір)
    st.markdown("<h2 style='color: #fab387;'>ДИСКЛЕЙМЕР</h2>", unsafe_allow_html=True)

    # HTML-блок із попередженням
    st.markdown("""
        <div class="disclaimer-box">
            <h2 style='color: #f38ba8; margin-top: 0;'>УВАГА КОД ПИСАЛА ЖІНКА‼️</h2>
            <p style='font-size: 18px; color: #cdd6f4;'>
                Це <b>СУПЕР пробна версія</b>. Шанс отримати дибільне слово <b>70%</b>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Кнопка підтвердження дисклеймера
    if st.button("ЛАДНО ✅"):
        # Перемикаємо стан гри на tutorial
        st.session_state.game_state = "tutorial"

        # Повний rerun застосунку
        st.rerun()


# -------------------------------------------------
# TUTORIAL / ЯК ГРАТИ
# -------------------------------------------------
elif st.session_state.game_state == "tutorial":

    # Заголовок екрану
    st.title("📖 Куди жмать? (методичка)")

    # Ділимо екран на 2 колонки
    col1, col2 = st.columns(2)

    # Ліва колонка — IRL режим
    with col1:
        st.markdown(
            "### 🏠 Режим IRL\n"
            "**Для тих, хто в одній кімнаті:**\n"
            "* Один телефон на всіх.\n"
            "* Передаєте мобілу тому, чия черга.\n"
            "* Тиснете **'Я готовий'** і вперед!"
        )

    # Права колонка — Discord режим
    with col2:
        st.markdown(
            "### 🎙️ DISCORD\n"
            "**Для гри на відстані:**\n"
            "* Кожен заходить зі свого девайсу.\n"
            "* Один створює кімнату (Начальнік), інші вводять код.\n"
            "* Система сама каже, хто пояснює."
        )

    # Інформаційний блок із головним правилом гри
    st.info(
        "💡 **Головне правило:** "
        "Пояснюй як хочеш, але не називай саме слово або спільнокореневі."
    )

    # Додатковий текст під правилами
    st.write(
        "➕ У налаштуваннях можна додати свої слова! "
        "(ми ще не розібралися як вони зберігаються, але обовʼязково пофіксимо). "
        "p.s: при натисканні вас флешне, будьте готові)))"
    )

    # Кнопка переходу далі
    if st.button("ЗРОЗУМІВ, ПОГНАЛИ! 🚀"):
        # Переходимо на екран вибору режиму
        st.session_state.game_state = "mode_select"
        st.rerun()


# -------------------------------------------------
# MODE SELECT / ВИБІР РЕЖИМУ
# -------------------------------------------------
elif st.session_state.game_state == "mode_select":

    # Заголовок
    st.title("🕹️ Оберіть режим гри")

    # Дві колонки для плиток режимів
    col1, col2 = st.columns(2)

    # IRL режим — посилання з query-параметром
    with col1:
        st.markdown(
            '<a href="/?mode=irl" target="_self" style="text-decoration: none;">'
            '<div class="mode-selection">'
            '<h3>🏠 IRL</h3>'
            '<p>Командна гра вживу</p>'
            '</div>'
            '</a>',
            unsafe_allow_html=True
        )

    # Discord режим
    with col2:
        st.markdown(
            '<a href="/?mode=discord" target="_self" style="text-decoration: none;">'
            '<div class="mode-selection">'
            '<h3>🎙️ DISCORD</h3>'
            '<p>Грайте разом онлайн</p>'
            '</div>'
            '</a>',
            unsafe_allow_html=True
        )

    # Візуальний роздільник
    st.divider()

    # Центрована кнопка повернення до tutorial
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("❓ Я ЗАБУВ ЯК РУЛИТЬ", use_container_width=True):
            st.session_state.game_state = "tutorial"
            st.rerun()


# -------------------------------------------------
# SETUP / НАЛАШТУВАННЯ ГРИ
# -------------------------------------------------
elif st.session_state.game_state == "setup":

    # Кнопка повернення назад
    if st.button("⬅️ НАЗАД"):
        st.session_state.game_state = "mode_select"
        st.rerun()

    # Заголовок налаштувань
    st.markdown("### ⚙️ Налаштування")


    # =============================================
    # DISCORD-РЕЖИМ
    # =============================================
    if st.session_state.game_mode == "discord":

        # Поле введення ніку користувача
        my_name = st.text_input(
            "Твій нікнейм:",
            placeholder="Введи шось прикольне...",
            key="setup_name"
        )

        # Роздільник
        st.divider()

        # Дві колонки: створити кімнату / увійти
        col1, col2 = st.columns(2)

        # ---------- СТВОРЕННЯ КІМНАТИ ----------
        with col1:

            # Підпис над кнопкою
            st.markdown(
                "<p style='text-align: center; font-weight: bold;'>Ти хостити будеш?</p>",
                unsafe_allow_html=True
            )

            # Фіктивний відступ для вирівнювання
            st.markdown("<div style='height: 57px;'></div>", unsafe_allow_html=True)

            # Кнопка створення кімнати
            if st.button("СТВОРИТИ КІМНАТУ ✨"):

                # Перевірка, що нік введений
                if my_name:

                    # Генеруємо ID кімнати
                    r_id = generate_room_code()

                    # Зберігаємо ID та ім'я в session_state
                    st.session_state.room_id = r_id
                    st.session_state.my_name = my_name

                    # Якщо Firestore підключений
                    if db:
                        # Створюємо документ кімнати
                        db.collection("rooms").document(r_id).set({
                            "host": my_name,                 # Хост кімнати
                            "players": [my_name],           # Список гравців
                            "scores": {my_name: 0},         # Очки
                            "state": "lobby",               # Поточний стан
                            "total_rounds": 3,              # Раунди
                            "duration": 60,                 # Таймер
                            "current_round": 1,             # Поточний раунд
                            "explainer": "",                # Пояснює
                            "listener": "",                 # Вгадує
                            "word": ""                      # Поточне слово
                        })

                        # Переходимо в синхронізоване лобі
                        st.session_state.game_state = "sync_lobby"
                        st.rerun()
                else:
                    # Якщо нік не введений
                    st.error("Спочатку введи нікнейм!")


        # ---------- ВХІД У КІМНАТУ ----------
        with col2:

            # Підпис
            st.markdown(
                "<p style='text-align: center; font-weight: bold;'>Маєш код?</p>",
                unsafe_allow_html=True
            )

            # Поле введення коду
            enter_code = st.text_input(
                "Введи код:",
                placeholder="Код тут...",
                label_visibility="collapsed",
                key="join_input_sync"
            ).upper().strip()  # Одразу приводимо код до нормального вигляду

            # Кнопка входу
            if st.button("УВІЙТИ 🚪"):

                # Перевірка, що є і нік, і код
                if my_name and enter_code:

                    # Якщо Firestore доступний
                    if db:
                        ref = db.collection("rooms").document(enter_code)
                        doc = ref.get()

                        # Якщо кімната існує
                        if doc.exists:
                            data = doc.to_dict()

                            # Зберігаємо локально
                            st.session_state.room_id = enter_code
                            st.session_state.my_name = my_name

                            # Якщо гравець ще не в кімнаті
                            if my_name not in data["players"]:
                                data["players"].append(my_name)
                                data["scores"][my_name] = 0

                                # Оновлюємо дані в Firestore
                                ref.update({
                                    "players": data["players"],
                                    "scores": data["scores"]
                                })

                            # Переходимо в лобі
                            st.session_state.game_state = "sync_lobby"
                            st.rerun()
                        else:
                            # Кімната не знайдена
                            st.error("❌ Код невірний!")
                else:
                    # Не введені обовʼязкові поля
                    st.error("Введи нік та код!")


    # =============================================
    # IRL-РЕЖИМ
    # =============================================
    elif st.session_state.game_mode == "irl":

        # Підзаголовок
        st.subheader("🏠 Налаштування гри вживу")

        # Слайдер кількості команд
        num = st.slider("Кількість команд?", 2, 6, 2)

        # Масив назв команд
        names = []

        # Дві колонки для введення назв
        c_names = st.columns(2)

        # Цикл по кількості команд
        for i in range(num):
            with c_names[i % 2]:
                name = st.text_input(
                    f"Команда {i + 1}",
                    f"Команда {i + 1}",
                    key=f"n_{i}"
                )
                names.append(name)

        # Роздільник
        st.divider()

        # Колонки для раундів і таймера
        col_r, col_t = st.columns(2)

        with col_r:
            rounds = st.number_input("Кількість раундів", 1, 20, 3)

        with col_t:
            timer = st.slider("Секунди на хід", 10, 120, 60)

        # Роздільник
        st.divider()

        # Кнопка старту гри
        if st.button("🔥 ПОЧАТИ ГРУ"):

            # Перевірка, що всі назви команд заповнені
            if any(n.strip() == "" for n in names):
                st.error("Всі команди повинні мати назву!")
            else:
                # Зберігаємо гравців
                st.session_state.players = names

                # Обнуляємо очки
                st.session_state.scores = {n: 0 for n in names}

                # Налаштування раундів і таймера
                st.session_state.total_rounds = rounds
                st.session_state.duration = timer

                # Початкові індекси
                st.session_state.current_player_idx = 0
                st.session_state.current_round = 1

                # Переходимо до гри
                st.session_state.game_state = "playing_irl"
                st.rerun()
# --- ДОДАВАННЯ СЛІВ ---
st.divider()  # візуальний роздільник, чисто щоб не було каші на сторінці

with st.expander("➕ Додати своє слово"):  # згортаний блок для додавання слів
    # показує кількість слів, які зараз є у словнику (береться із session_state)
    st.info(f"Зараз у словнику слів: {len(st.session_state.all_words)}")

    # поле введення слова
    # key потрібен, щоб Streamlit знав, що це саме цей інпут
    new_word_raw = st.text_input("Введи слово:", key="input_field")

    # кнопка, яка тригерить логіку додавання
    if st.button("ДОДАТИ В СЛОВНИК"):

        # прибираємо пробіли по краях + робимо першу літеру великою
        word = new_word_raw.strip().capitalize()

        # те саме слово, але в lower — для перевірки на дубль
        low_word = word.lower()

        # список усіх слів у lower, щоб порівнювати без врахування регістру
        existing_low = [w.lower() for w in st.session_state.all_words]

        # перевірка, що інпут не порожній
        if word != "":
            # якщо слово вже є (без врахування регістру)
            if low_word in existing_low:
                # записуємо повідомлення про помилку в session_state
                st.session_state.msg_data = {
                    "text": "Таке слово вже є!",
                    "type": "error"
                }
            else:
                # додаємо слово в список слів
                st.session_state.all_words.append(word)

                # зберігаємо останнє додане слово
                st.session_state.last_added_word = word

                # записуємо success-повідомлення
                st.session_state.msg_data = {
                    "text": "Слово додано!",
                    "type": "success"
                }

                # фізично дописуємо слово у файл
                append_word_to_file(word)

            # примусовий перерендер сторінки,
            # щоб оновились список слів і повідомлення
            st.rerun()

    # якщо є текст повідомлення — показуємо його
    if st.session_state.msg_data["text"]:
        # якщо тип success — зелений алерт
        if st.session_state.msg_data["type"] == "success":
            st.success(st.session_state.msg_data["text"])
        # інакше — червоний алерт
        else:
            st.error(st.session_state.msg_data["text"])

    # якщо є останнє додане слово — показуємо його під формою
    if st.session_state.last_added_word:
        st.markdown(f"✅ Останнє: **{st.session_state.last_added_word}**")
# --- СИНХРОНІЗОВАНЕ ЛОББІ (DISCORD) ---
elif st.session_state.game_state == "sync_lobby":
    # Заголовок з кодом кімнати
    st.title(f"🏠 Кімната: {st.session_state.room_id}")

    # Посилання на документ кімнати в Firestore
    ref = db.collection("rooms").document(st.session_state.room_id)
    doc = ref.get()

    # Якщо кімната існує в базі
    if doc.exists:
        # Дістаємо всі дані кімнати
        data = doc.to_dict()

        # Поточний список гравців
        current_players = data.get("players", [])

        # Моє імʼя з session_state
        my_name = st.session_state.my_name

        # Перевірка, чи я хост
        is_host = (data.get("host") == my_name)

        # --- СПОВІЩЕННЯ ПРО ВХІД / ВИХІД ГРАВЦІВ ---
        # Якщо це перший рендер — запамʼятовуємо поточний список
        if "old_players" not in st.session_state:
            st.session_state.old_players = current_players

        # Якщо хтось новий зʼявився — тост
        for p in current_players:
            if p not in st.session_state.old_players:
                st.toast(f"✨ {p} приєднався до гри!")

        # Якщо хтось зник — тост
        for p in st.session_state.old_players:
            if p not in current_players:
                st.toast(f"🚪 {p} лівнув з катки...")

        # Оновлюємо старий список гравців
        st.session_state.old_players = current_players

        # --- САЙДБАР ЛОББІ ---
        with st.sidebar:
            # Код кімнати
            st.write(f"🏠 Код: **{st.session_state.room_id}**")

            # Моє імʼя + іконка хоста
            st.write(f"👤 Ти: **{my_name}** {'(👑)' if is_host else ''}")

            st.divider()

            # Список гравців
            st.write("👥 Гравці:")
            for p in current_players:
                st.caption(f"• {p} {'(Хост)' if p == data.get('host') else ''}")

            # Кнопка виходу з гри
            if st.button("🔴 ВИЙТИ З ГРИ", key="exit_btn"):
                # Видаляємо себе зі списку гравців
                updated_players = [p for p in current_players if p != my_name]
                ref.update({"players": updated_players})

                # Чистимо room_id
                del st.session_state.room_id

                # Повертаємось у головне меню
                st.session_state.game_state = "mode_select"
                st.rerun()

    # ⚠️ Логічна помилка: цей elif ніколи не виконається,
    # бо перевіряє те саме, що й if вище
    elif doc.exists:
        st.error("Кімнату не знайдено!")
        st.session_state.game_state = "setup"
        st.rerun()

    # Повторно дістаємо дані кімнати
    data = doc.to_dict()

    # Якщо хост уже запустив гру — всі переходять у playing_sync
    if data.get("state") == "playing":
        st.session_state.game_state = "playing_sync"
        st.rerun()

    # --- ОСНОВНИЙ ЕКРАН ЛОББІ ---
    st.write("### Гравці в лобі:")

    # Відображення гравців у 3 колонки
    cols = st.columns(3)
    for i, p in enumerate(data["players"]):
        cols[i % 3].button(f"👤 {p}", disabled=True, key=f"p_{i}")

    st.divider()

    # Повторна перевірка, чи я хост
    is_host = (data.get("host") == st.session_state.my_name)

    if is_host:
        # Налаштування для хоста
        st.subheader("👑 Ви Хост (Адмін)")

        # Кількість раундів
        h_rounds = st.number_input(
            "Кількість раундів",
            1, 20,
            data.get("total_rounds", 3),
            key="host_rounds_sync"
        )

        # Час на хід
        h_timer = st.slider(
            "Секунди на хід",
            10, 120,
            data.get("duration", 60)
        )

        # Якщо значення змінилися — оновлюємо базу
        if h_rounds != data.get("total_rounds") or h_timer != data.get("duration"):
            ref.update({"total_rounds": h_rounds, "duration": h_timer})

        # Кнопка старту гри
        if st.button("ПОЧАТИ ГРУ ДЛЯ ВСІХ 🔥"):
            ref.update({
                "state": "playing",
                "current_round": 1,
                "explainer": "",
                "listener": ""
            })
            st.rerun()
    else:
        # Повідомлення для не-хостів
        st.warning("🕒 Очікуємо, поки хост розбереться в кнопках...")
        st.info(f"📊 Раундів: {data.get('total_rounds', 3)} | ⏱ Час: {data.get('duration', 60)}с")

    # Кнопка виходу з кімнати (дублюється поза сайдбаром)
    if st.button("🚪 ПОКИНУТИ КІМНАТУ"):
        updated_players = [p for p in current_players if p != my_name]
        ref.update({"players": updated_players})
        del st.session_state.room_id
        st.session_state.game_state = "mode_select"
        st.rerun()

    # Автооновлення лоббі
    time.sleep(2)
    st.rerun()
elif st.session_state.game_state == "playing_sync":
    # Гра в синхронному режимі, тут обробляємо активний хід та очікування

    # 1. Отримуємо свіжі дані з бази Firestore
    ref = db.collection("rooms").document(st.session_state.room_id)  # посилання на документ кімнати
    doc = ref.get()  # отримуємо дані з бази

    if not doc.exists:
        # Якщо документа нема (кімната видалена/не створена), повертаємо в головне меню
        st.session_state.game_state = "mode_select"
        st.rerun()

    data = doc.to_dict()  # конвертуємо дані документа у словник
    total_rounds = data.get("total_rounds", 3)  # загальна кількість раундів
    current_round = data.get("current_round", 1)  # поточний раунд
    my_name = st.session_state.my_name  # ім'я гравця
    is_host = (data.get("host") == my_name)  # перевірка, чи ми хост

    # 2. Перевірка на фінал гри
    if current_round > total_rounds:
        st.session_state.scores = data.get("scores", {})  # зберігаємо фінальні бали
        st.session_state.game_state = "finished"  # стан гри — завершено
        st.rerun()  # перезавантаження сторінки

    # ----------------------------
    # Стан 1: Очікування початку ходу
    # ----------------------------
    if not data.get("explainer"):  # якщо ще не обрано пояснювача
        st.title(f"Раунд {current_round} з {total_rounds}")  # заголовок раунду

        # масив "заповнювачів" та жартівливих підказок для гравців
        quotes = [
            "💡 Порада: якщо не знаєш слова - кажи що всі інші безнадійні і теж не знають та скіпай!",
            "⏳ Очікуємо... Тим часом придумай, як пояснити слово 'Бебра'.",
            "📐 4(x - 5) = 3x - 6",
            "😁 Ми теж не знаємо що таке Барбадос."
        ]

        st.info(random.choice(quotes))  # виводимо випадкову підказку/жарт

        if is_host:  # якщо ми хост
            if st.button("ПОЧАТИ ХІД 🎲", use_container_width=True):
                current_players = data.get("players", [])  # список гравців
                if len(current_players) >= 2:  # мінімум 2 гравці для ходу
                    p1, p2 = random.sample(current_players, 2)  # випадково обираємо пару
                    print(f"[GAME] Host picked: {p1} explaining to {p2}")  # лог в консоль
                    ref.update({
                        "explainer": p1,  # пояснювач
                        "listener": p2,   # той, хто відгадує
                        "word": random.choice(st.session_state.all_words),  # випадкове слово
                        "t_end": time.time() + data.get("duration", 60)  # кінець таймера
                    })
                    st.rerun()  # перезавантаження сторінки
                else:
                    st.error("Для гри потрібно мінімум 2 гравці!")  # помилка, якщо мало гравців
        else:
            # якщо ми не хост — чекаємо, поки хост запустить хід
            st.warning("⏳ Очікуємо, поки хост запустить наступний хід...")
            time.sleep(2)
            st.rerun()

    # ----------------------------
    # Стан 2: Активний хід (таймер та слова)
    # ----------------------------
    else:  # якщо вже обрано пояснювача
        rem = int(data["t_end"] - time.time())  # залишок часу

        if rem <= 0:  # якщо час вийшов
            ref.update({
                "explainer": "",  # скидаємо пояснювача
                "listener": ""    # скидаємо слухача
            })
            st.warning("⏰ Час вийшов!")  # повідомлення про кінець таймера

            if is_host:  # хост може переключити хід
                if st.button("НАСТУПНИЙ ХІД ➡️", use_container_width=True):
                    ref.update({
                        "word": "",  # скидаємо слово
                        "current_round": current_round + 1 if is_host else current_round  # наступний раунд
                    })
                    st.rerun()
            else:
                # інші гравці чекають на хост
                st.info("🕒 Очікуємо, поки хост переключить раунд...")
                time.sleep(2)
                st.rerun()
        else:
            # якщо час ще є
            st.subheader(f"⏱ Залишилось: {rem} сек")  # показуємо таймер
            st.write(f"🎤 Пояснює: **{data['explainer']}** ➜ Слухає: **{data['listener']}**")  # хто пояснює, хто слухає

            if my_name == data["explainer"]:  # якщо ми пояснювач
                st.success("ТВОЯ ЧЕРГА ПОЯСНЮВАТИ!")
                st.markdown(f'<div class="word-box">{data["word"].upper()}</div>', unsafe_allow_html=True)  # показ слова

                c1, c2 = st.columns(2)  # дві кнопки: вгадано / пропустити
                if c1.button("✅ ВГАДАНО", use_container_width=True):
                    # оновлюємо бали в базі
                    new_scores = data.get("scores", {})
                    new_scores[my_name] = new_scores.get(my_name, 0) + 1
                    ref.update({
                        "scores": new_scores,
                        "word": random.choice(st.session_state.all_words)  # нове слово
                    })
                    st.rerun()

                if c2.button("❌ ПРОПУСТИТИ", use_container_width=True):
                    ref.update({"word": random.choice(st.session_state.all_words)})  # нове слово
                    st.rerun()

            elif my_name == data["listener"]:  # якщо ми слухач
                st.warning("ТИ ВІДГАДУЄШ!")
                st.markdown('<div class="word-box">???</div>', unsafe_allow_html=True)  # слово приховане

            else:  # інші гравці просто спостерігають
                st.info("Спостерігайте за грою інших...")
                st.markdown(f'<div class="word-box" style="font-size: 24px;">{data["explainer"]} пояснює...</div>',
                            unsafe_allow_html=True)

            time.sleep(1)  # пауза 1 секунда перед оновленням
            st.rerun()  # постійне оновлення сторінки для синхронності
# --- IRL РЕЖИМ ---  (гра в реальному житті, локально, без синхронізації через базу)
elif st.session_state.game_state == "playing_irl":

    # Перевірка на завершення гри
    if st.session_state.current_round > st.session_state.total_rounds:
        st.session_state.game_state = "finished"  # якщо раунди закінчились — гра завершена
        st.rerun()  # перезавантаження сторінки, щоб перейти у фінал

    # Хто зараз активний гравець
    active = st.session_state.players[st.session_state.current_player_idx]

    # Якщо черга ще не активна
    if 'turn_active' not in st.session_state or not st.session_state.turn_active:
        st.title(f"Раунд {st.session_state.current_round} з {st.session_state.total_rounds}")  # заголовок раунду
        st.subheader(f"Черга: {active}")  # показуємо, хто зараз пояснює
        if st.button("Я ГОТОВИЙ! ▶️"):  # кнопка гравця, що він готовий почати
            st.session_state.turn_active = True  # встановлюємо стан ходу як активний
            st.session_state.start_time = time.time()  # записуємо час старту ходу
            st.session_state.current_word = random.choice(st.session_state.all_words);  # обираємо слово для пояснення
            st.rerun()  # перезавантаження сторінки для старту ходу

    # Якщо хід активний
    else:
        # залишок часу для поточного ходу
        rem = int(st.session_state.duration - (time.time() - st.session_state.start_time))

        # якщо час вийшов
        if rem <= 0:
            st.session_state.turn_active = False  # хід закінчився
            # переходимо до наступного гравця (циклічно)
            st.session_state.current_player_idx = (st.session_state.current_player_idx + 1) % len(
                st.session_state.players)
            # якщо всі гравці вже грали в цьому раунді, збільшуємо номер раунду
            if st.session_state.current_player_idx == 0: st.session_state.current_round += 1
            st.rerun()  # перезавантаження сторінки для нового ходу або нового раунду

        # Вивід таймера і активного гравця
        st.subheader(f"⏱ {rem} сек | {active}")
        # Показуємо слово, яке треба пояснити
        st.markdown(f'<div class="word-box">{st.session_state.current_word.upper()}</div>', unsafe_allow_html=True)

        # Дві кнопки: "Вгадано" та "Скіп"
        c1, c2 = st.columns(2)
        if c1.button("✅ ВГАДАНО"):
            st.session_state.scores[active] += 1;  # додаємо бал активному гравцю
            st.session_state.current_word = random.choice(st.session_state.all_words);  # нове слово
            st.rerun()  # перезавантаження сторінки

        if c2.button("❌ СКІП"):
            st.session_state.current_word = random.choice(st.session_state.all_words);  # нове слово без балів
            st.rerun()

        time.sleep(0.1);  # невелика пауза, щоб уникнути "зависаючих" оновлень
        st.rerun()  # постійне оновлення сторінки для таймера

# --- ФІНАЛ ---  (коли гра завершена)
elif st.session_state.game_state == "finished":
    st.balloons();  # веселий ефект
    st.title("🏆 РЕЗУЛЬТАТИ")  # заголовок фіналу
    # Виводимо всіх гравців у порядку балів (від більшого до меншого)
    for n, s in sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True):
        st.write(f"### {n}: {s} балів")  # ім'я та кількість балів

    # Кнопка повернення у головне меню
    if st.button("В ГОЛОВНЕ МЕНЮ 🔄"):
        st.session_state.game_state = "mode_select";  # змінюємо стан гри на головне меню
        st.rerun()  # перезавантаження сторінки




#фікс нового багу з раундами і вильотом
        
elif st.session_state.game_state == "playing_sync":  # Перевіряємо, чи ми зараз в синхронній онлайн грі
    # 1. Отримуємо свіжі дані з бази
    ref = db.collection("rooms").document(st.session_state.room_id)  # Створюємо посилання на документ кімнати в Firestore
    doc = ref.get()  # Отримуємо актуальні дані з бази
    if not doc.exists:  # Якщо документа не існує
        st.session_state.game_state = "mode_select"  # Повертаємо користувача в головне меню
        st.rerun()  # Перезапускаємо Streamlit для оновлення UI

    data = doc.to_dict()  # Перетворюємо дані документа у словник Python
    total_rounds = data.get("total_rounds", 3)  # Загальна кількість раундів, дефолт 3
    current_round = data.get("current_round", 1)  # Поточний раунд, дефолт 1
    my_name = st.session_state.my_name  # Ім'я поточного гравця
    is_host = (data.get("host") == my_name)  # Перевірка, чи я хост

    # Перевірка на фінал гри
    if current_round > total_rounds:  # Якщо поточний раунд більше загальної кількості
        st.session_state.scores = data.get("scores", {})  # Записуємо фінальні бали
        st.session_state.game_state = "finished"  # Перемикаємо стан гри на "фініш"
        st.rerun()  # Оновлюємо UI

    # --- Стан 1: Очікування початку ходу (вибір пари) ---
    if not data.get("explainer"):  # Якщо ще немає активного пояснювача
        st.title(f"Раунд {current_round} з {total_rounds}")  # Виводимо номер раунду

        # Обираємо рандомний quote лише один раз для цього раунду
        if "current_quote" not in st.session_state:  # Перевіряємо, чи вже є quote
            st.session_state.current_quote = random.choice(st.session_state.quotes)  # Вибираємо випадковий
        st.info(st.session_state.current_quote)  # Показуємо обраний quote

        if is_host:  # Якщо я хост
            if st.button("ПОЧАТИ ХІД 🎲", use_container_width=True):  # Кнопка запуску ходу
                current_players = data.get("players", [])  # Отримуємо список гравців
                if len(current_players) >= 2:  # Перевірка на мінімум 2 гравців
                    p1, p2 = random.sample(current_players, 2)  # Випадково обираємо пояснювача і слухача
                    ref.update({  # Оновлюємо документ у базі
                        "explainer": p1,  # Хто пояснює
                        "listener": p2,  # Хто слухає
                        "word": random.choice(st.session_state.all_words),  # Слово для пояснення
                        "t_end": time.time() + data.get("duration", 60)  # Кінець ходу через duration секунд
                    })
                    time.sleep(0.05)  # Коротка пауза для синхронізації з базою
                    st.rerun()  # Оновлюємо UI
                else:
                    st.error("Для гри потрібно мінімум 2 гравці!")  # Виводимо помилку
        else:
            st.warning("⏳ Очікуємо, поки хост запустить наступний хід...")  # Якщо не хост, чекаємо
            time.sleep(0.5)  # Коротка пауза
            st.rerun()  # Оновлюємо UI

    # --- Стан 2: Активний хід (таймер і слова) ---
    else:
        # Підтягуємо свіжі дані перед відображенням
        doc = ref.get()  # Беремо останні дані з бази
        data = doc.to_dict()  # Конвертуємо в словник
        current_round = data.get("current_round", 1)  # Підтягуємо актуальний номер раунду

        rem = int(data["t_end"] - time.time())  # Обчислюємо залишок часу
        if rem <= 0:  # Якщо час вийшов
            # Знімаємо активного гравця і збільшуємо раунд, якщо хост
            updates = {"explainer": "", "listener": ""}  # Очищаємо пояснювача і слухача
            if is_host:
                updates["current_round"] = current_round + 1  # Хост збільшує раунд
            ref.update(updates)  # Оновлюємо документ у базі
            st.session_state.current_quote = None  # Обнуляємо quote для нового раунду
            time.sleep(0.05)  # Невелика пауза
            st.rerun()  # Перезапуск UI
        else:
            st.subheader(f"⏱ Залишилось: {rem} сек | Раунд {current_round}")  # Показуємо таймер і раунд
            st.write(f"🎤 Пояснює: **{data['explainer']}** ➜ Слухає: **{data['listener']}**")  # Інформація про хід

            if my_name == data["explainer"]:  # Якщо я пояснювач
                st.success("ТВОЯ ЧЕРГА ПОЯСНЮВАТИ!")  # Виводимо повідомлення
                st.markdown(f'<div class="word-box">{data["word"].upper()}</div>', unsafe_allow_html=True)  # Слово для пояснення

                c1, c2 = st.columns(2)  # Розділяємо кнопку на дві колонки
                if c1.button("✅ ВГАДАНО", use_container_width=True):  # Кнопка вгадано
                    new_scores = data.get("scores", {})  # Беремо поточні бали
                    new_scores[my_name] = new_scores.get(my_name, 0) + 1  # Додаємо 1 бал
                    ref.update({  # Оновлюємо базу
                        "scores": new_scores,
                        "word": random.choice(st.session_state.all_words)  # Нове слово
                    })
                    time.sleep(0.05)  # Пауза для синхронізації
                    st.rerun()  # Перезапуск UI

                if c2.button("❌ ПРОПУСТИТИ", use_container_width=True):  # Кнопка пропустити
                    ref.update({"word": random.choice(st.session_state.all_words)})  # Нове слово
                    time.sleep(0.05)
                    st.rerun()

            elif my_name == data["listener"]:  # Якщо я слухач
                st.warning("ТИ ВІДГАДУЄШ!")  # Повідомлення
                st.markdown('<div class="word-box">???</div>', unsafe_allow_html=True)  # Слово приховано

            else:  # Якщо я спостерігач
                st.info("Спостерігайте за грою інших...")  # Повідомлення
                st.markdown(f'<div class="word-box" style="font-size: 24px;">{data["explainer"]} пояснює...</div>',
                            unsafe_allow_html=True)  # Відображаємо, хто пояснює

            time.sleep(0.1)  # Коротка пауза перед повторним rerun
            st.rerun()  # Перезапуск UI для оновлення таймера та стану




#фікс квот можливо
# --- Стан 1: Очікування початку ходу (вибір пари) ---
if not data.get("explainer"):  # Якщо ще немає активного пояснювача
    st.title(f"Раунд {current_round} з {total_rounds}")  # Виводимо номер раунду

    # --- Вибір рандомного quote ---
    # Ми хочемо, щоб кожен раунд показував **один quote**, а не мінявся кожну секунду
    if "current_quote" not in st.session_state:  # Перевіряємо, чи вже обраний quote для цього раунду
        st.session_state.current_quote = random.choice(st.session_state.quotes)  
        # Якщо ще немає, вибираємо випадковий і зберігаємо в session_state,
        # щоб він залишався постійним для всіх учасників і не змінювався при rerun

    st.info(st.session_state.current_quote)  # Відображаємо обраний quote на екрані

    # --- Кнопка старту ходу для хоста ---
    if is_host:  
        if st.button("ПОЧАТИ ХІД 🎲", use_container_width=True):  # Якщо хост натискає кнопку
            current_players = data.get("players", [])  # Беремо список гравців
            if len(current_players) >= 2:  # Перевірка на мінімум 2 гравців
                p1, p2 = random.sample(current_players, 2)  # Випадковий пояснювач і слухач
                ref.update({  # Оновлюємо базу
                    "explainer": p1,
                    "listener": p2,
                    "word": random.choice(st.session_state.all_words),
                    "t_end": time.time() + data.get("duration", 60)
                })
                time.sleep(0.05)  # Невелика пауза для синхронізації
                st.rerun()  # Оновлюємо UI
            else:
                st.error("Для гри потрібно мінімум 2 гравці!")  # Повідомлення про помилку
    else:
        st.warning("⏳ Очікуємо, поки хост запустить наступний хід...")  # Якщо не хост, чекаємо
        time.sleep(0.5)  # Коротка пауза для стабільності
        st.rerun()  # Оновлення UI



#фікс екранів раунду квот виліт гравця МОЖЛИВИЙ все разом
elif st.session_state.game_state == "playing_sync":
    # --- Отримуємо свіжі дані з бази ---
    ref = db.collection("rooms").document(st.session_state.room_id)
    doc = ref.get()
    if not doc.exists:
        # Якщо кімнати не існує — повертаємося в меню вибору режиму
        st.session_state.game_state = "mode_select"
        st.rerun()

    data = doc.to_dict()
    total_rounds = data.get("total_rounds", 3)
    current_round = data.get("current_round", 1)  # номер поточного раунду
    my_name = st.session_state.my_name
    is_host = (data.get("host") == my_name)

    # --- Перевірка на фінал гри ---
    if current_round > total_rounds:
        st.session_state.scores = data.get("scores", {})
        st.session_state.game_state = "finished"
        st.rerun()

    # --- Стан 1: Очікування початку ходу (вибір пари) ---
    if not data.get("explainer"):
        st.title(f"Раунд {current_round} з {total_rounds}")

        # --- Вибір статичного quote, прив'язка до раунду ---
        if ("current_quote" not in st.session_state or
            st.session_state.get("quote_round", 0) != current_round):
            st.session_state.current_quote = random.choice(st.session_state.quotes)
            st.session_state.quote_round = current_round
        st.info(st.session_state.current_quote)

        if is_host:
            if st.button("ПОЧАТИ ХІД 🎲", use_container_width=True):
                current_players = data.get("players", [])
                if len(current_players) >= 2:
                    # Рандомно обираємо двох гравців для пояснення/відгадування
                    p1, p2 = random.sample(current_players, 2)
                    ref.update({
                        "explainer": p1,
                        "listener": p2,
                        "word": random.choice(st.session_state.all_words),
                        "t_end": time.time() + data.get("duration", 60)
                    })
                    # Маленька пауза, щоб база оновилася перед rerun
                    time.sleep(0.05)
                    st.rerun()
                else:
                    st.error("Для гри потрібно мінімум 2 гравці!")
        else:
            st.warning("⏳ Очікуємо, поки хост запустить наступний хід...")
            time.sleep(0.5)
            st.rerun()

    # --- Стан 2: Активний хід (таймер і слова) ---
    else:
        # Завжди підтягуємо свіжі дані перед відображенням
        doc = ref.get()
        data = doc.to_dict()
        current_round = data.get("current_round", 1)

        rem = int(data["t_end"] - time.time())
        if rem <= 0:
            # Знімаємо активного гравця і збільшуємо раунд, якщо хост
            updates = {"explainer": "", "listener": ""}
            if is_host:
                updates["current_round"] = current_round + 1
            ref.update(updates)

            # Обнуляємо quote для наступного раунду
            st.session_state.current_quote = None
            st.session_state.quote_round = 0
            # Маленька пауза для оновлення
            time.sleep(0.05)
            st.rerun()
        else:
            # Відображаємо таймер та поточний раунд
            st.subheader(f"⏱ Залишилось: {rem} сек | Раунд {current_round}")
            st.write(f"🎤 Пояснює: **{data['explainer']}** ➜ Слухає: **{data['listener']}**")

            # --- Дії для пояснювача ---
            if my_name == data["explainer"]:
                st.success("ТВОЯ ЧЕРГА ПОЯСНЮВАТИ!")
                st.markdown(f'<div class="word-box">{data["word"].upper()}</div>', unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                if c1.button("✅ ВГАДАНО", use_container_width=True):
                    # Оновлюємо бали в базі
                    new_scores = data.get("scores", {})
                    new_scores[my_name] = new_scores.get(my_name, 0) + 1
                    ref.update({
                        "scores": new_scores,
                        "word": random.choice(st.session_state.all_words)
                    })
                    time.sleep(0.05)
                    st.rerun()

                if c2.button("❌ ПРОПУСТИТИ", use_container_width=True):
                    ref.update({"word": random.choice(st.session_state.all_words)})
                    time.sleep(0.05)
                    st.rerun()

            # --- Дії для відгадувача ---
            elif my_name == data["listener"]:
                st.warning("ТИ ВІДГАДУЄШ!")
                st.markdown('<div class="word-box">???</div>', unsafe_allow_html=True)

            # --- Дії для спостерігачів ---
            else:
                st.info("Спостерігайте за грою інших...")
                st.markdown(
                    f'<div class="word-box" style="font-size: 24px;">{data["explainer"]} пояснює...</div>',
                    unsafe_allow_html=True
                )

            # Коротка пауза, щоб уникнути "викиду" і проблем з ререндером
            time.sleep(0.1)
            st.rerun()
