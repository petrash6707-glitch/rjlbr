import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Файл для сохранения данных
DATA_FILE = "warehouse_data.json"

# Данные по умолчанию
default_data = {
    "warehouse_city": {
        "Malasian x Protest - Виноград мармелад": 3,
        "Malasian x Protest - Кола ваниль": 2,
        "Malasian x Protest - Красные лесные ягоды": 3,
        "Malasian x Protest - Лайм киви": 3,
        "Podonki Blood - Малиновый лимонад": 3,
        "Podonki Blood - Чёрная смородина": 3,
        "Анархия V2 Strong Лимонный мармелад": 2,
        "Анархия V2 Strong Клюква брусника": 2,
        "Монархия - Лимон виноград": 2,
        "Монархия - Малина лимон": 2,
        "MPAK & ЧЁ NADO - Арбуз малина": 3,
        "MPAK & ЧЁ NADO - Виноград мята": 3,
        "MPAK & ЧЁ NADO - Кислый персик": 3,
        "MPAK & ЧЁ NADO - Спрайт": 3,
        "Хаски на Аляске Hard - Вишня жимолость": 2,
        "Хаски на Аляске Hard - Черешня клюква": 2,
        "Хаски на Аляске Hard - Яблоко клюква": 2,
        "LOST MARY MO30000 - Кислый виноград лёд": 1,
        "LOST MARY OS12000 Виноград лимон лёд": 0,
        "LOST MARY OS12000 Леданая ежевика": 1,
        "Malasian x Protest - Маракуйя зелёное яблок": 2,
        "Хаски на Аляске Hard - Ананас малина": 2,
        "Монархия - Смородиновые леденцы": 2,
        "Хаски на Аляске Hard - Красная смородина": 2
    },
    "warehouse_talovka": {
        "Malasian x Protest - Виноград мармелад": 1,
        "Malasian x Protest - Кола ваниль": 1,
        "Malasian x Protest - Красные лесные ягоды": 0,
        "Malasian x Protest - Лайм киви": 1,
        "Podonki Blood - Малиновый лимонад": 1,
        "Podonki Blood - Чёрная смородина": 1,
        "Анархия V2 Strong Лимонный мармелад": 1,
        "Анархия V2 Strong Клюква брусника": 1,
        "Монархия - Лимон виноград": 1,
        "Монархия - Малина лимон": 1,
        "MPAK & ЧЁ NADO - Арбуз малина": 1,
        "MPAK & ЧЁ NADO - Виноград мята": 1,
        "MPAK & ЧЁ NADO - Кислый персик": 1,
        "MPAK & ЧЁ NADO - Спрайт": 1,
        "Хаски на Аляске Hard - Вишня жимолость": 1,
        "Хаски на Аляске Hard - Черешня клюква": 1,
        "Хаски на Аляске Hard - Яблоко клюква": 1,
        "LOST MARY MO30000 - Кислый виноград лёд": 1,
        "LOST MARY OS12000 Виноград лимон лёд": 0,
        "LOST MARY OS12000 Ледяная ежевика": 1,
        "Malasian x Protest - Маракуйя зелёное яблоко": 2,
        "Хаски на Аляске Hard - Ананас малина": 2,
        "Монархия - Смородиновые леденцы": 2,
        "Хаски на Аляске Hard - Красная смородина": 2
    }
}

class WarehouseManager:
    def __init__(self):
        self.warehouse_city = {}
        self.warehouse_talovka = {}
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из файла"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.warehouse_city = data.get("warehouse_city", default_data["warehouse_city"])
                self.warehouse_talovka = data.get("warehouse_talovka", default_data["warehouse_talovka"])
                logger.info("Данные успешно загружены из файла")
            except Exception as e:
                logger.error(f"Ошибка загрузки данных: {e}")
                self.reset_to_default()
        else:
            self.reset_to_default()
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            data = {
                "warehouse_city": self.warehouse_city,
                "warehouse_talovka": self.warehouse_talovka
            }
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Данные успешно сохранены")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            return False
    
    def reset_to_default(self):
        """Сброс к данным по умолчанию"""
        self.warehouse_city = default_data["warehouse_city"].copy()
        self.warehouse_talovka = default_data["warehouse_talovka"].copy()
        self.save_data()
        logger.info("Данные сброшены к значениям по умолчанию")
    
    def register_sale(self, warehouse: str, product_name: str) -> bool:
        """Регистрация продажи товара"""
        if warehouse == "city":
            if self.warehouse_city.get(product_name, 0) > 0:
                self.warehouse_city[product_name] -= 1
                self.save_data()
                return True
        else:  # talovka
            if self.warehouse_talovka.get(product_name, 0) > 0:
                self.warehouse_talovka[product_name] -= 1
                self.save_data()
                return True
        return False

# Инициализация менеджера складов
warehouse_manager = WarehouseManager()

# Авторизованные пользователи
AUTHORIZED_USERS = ["@DexterNote", "@puffplace74"]  # Оба могут продавать
RESET_USERS = ["@puffplace74"]  # Только @puffplace74 может сбрасывать данные
NOTIFICATION_USER = "@puffplace74"  # Уведомления отправляются @puffplace74

# Текущие состояния пользователей
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📦 Посмотреть наличие", callback_data="view_stock")],
        [InlineKeyboardButton("💰 Регистрация продаж", callback_data="sales_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            "Добро пожаловать! Выберите раздел:",
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            "Добро пожаловать! Выберите раздел:",
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "view_stock":
        await show_warehouse_selection(query, "view")
    elif data == "sales_menu":
        if await check_authorization(query):
            await show_warehouse_selection(query, "sales")
        else:
            await query.edit_message_text("❌ У вас нет доступа к этому разделу")
    elif data == "back_to_main":
        await start(update, context)
    elif data == "back_to_warehouse_selection_view":
        await show_warehouse_selection(query, "view")
    elif data == "back_to_warehouse_selection_sales":
        await show_warehouse_selection(query, "sales")
    elif data.startswith("warehouse_"):
        _, action, warehouse = data.split("_")
        if action == "view":
            await show_stock(query, warehouse)
        elif action == "sales":
            user_states[user_id] = {"action": "select_product", "warehouse": warehouse}
            await show_products_for_sale(query, warehouse)
    elif data.startswith("product_"):
        _, warehouse, product_index = data.split("_")
        product_index = int(product_index)
        products = list(warehouse_manager.warehouse_city.keys()) if warehouse == "city" else list(warehouse_manager.warehouse_talovka.keys())
        
        if product_index < len(products):
            product_name = products[product_index]
            user_states[user_id] = {
                "action": "confirm_sale", 
                "warehouse": warehouse,
                "product": product_name
            }
            await confirm_sale(query, warehouse, product_name)
    elif data.startswith("confirm_"):
        _, warehouse, product_index, decision = data.split("_")
        product_index = int(product_index)
        products = list(warehouse_manager.warehouse_city.keys()) if warehouse == "city" else list(warehouse_manager.warehouse_talovka.keys())
        
        if product_index < len(products):
            product_name = products[product_index]
            
            if decision == "yes":
                # Регистрируем продажу
                success = warehouse_manager.register_sale(warehouse, product_name)
                
                if success:
                    # Отправляем уведомление @puffplace74
                    await send_sale_notification(context, query.from_user.username, warehouse, product_name)
                    
                    await query.edit_message_text(
                        f"✅ Продажа товара '{product_name}' зарегистрирована!\n"
                        f"Склад: {'Город' if warehouse == 'city' else 'Таловка'}\n\n"
                        f"Что дальше?",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔄 Еще продажа", callback_data=f"warehouse_sales_{warehouse}")],
                            [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")]
                        ])
                    )
                else:
                    await query.edit_message_text(
                        f"❌ Товара '{product_name}' нет в наличии!\n\n"
                        f"Что дальше?",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔄 Выбрать другой товар", callback_data=f"warehouse_sales_{warehouse}")],
                            [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")]
                        ])
                    )
            else:
                await query.edit_message_text(
                    "❌ Продажа отменена\n\nЧто дальше?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Выбрать другой товар", callback_data=f"warehouse_sales_{warehouse}")],
                        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")]
                    ])
                )
    elif data == "reset_data":
        if await check_reset_authorization(query):
            # Сброс к исходным данным
            warehouse_manager.reset_to_default()
            await query.edit_message_text(
                "✅ Данные сброшены к исходным значениям!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")]
                ])
            )
        else:
            await query.edit_message_text("❌ У вас нет доступа к этой функции")

async def send_sale_notification(context: ContextTypes.DEFAULT_TYPE, seller_username: str, warehouse: str, product_name: str) -> None:
    """Отправка уведомления о продаже @puffplace74"""
    try:
        stock_data = warehouse_manager.warehouse_city if warehouse == "city" else warehouse_manager.warehouse_talovka
        current_stock = stock_data[product_name]
        warehouse_name = "Город" if warehouse == "city" else "Таловка"
        
        seller_display = f"@{seller_username}" if seller_username else "Неизвестный пользователь"
        
        message = (
            f"💰 **Продажа зарегистрирована**\n\n"
            f"👤 Продавец: {seller_display}\n"
            f"📦 Товар: {product_name}\n"
            f"🏢 Склад: {warehouse_name}\n"
            f"📊 Осталось в наличии: {current_stock} шт."
        )
        
        # Здесь нужно указать chat_id пользователя @puffplace74
        # В реальном боте нужно получить chat_id этого пользователя
        # Пока отправляем в лог
        logger.info(f"Уведомление о продаже для {NOTIFICATION_USER}: {message}")
        
        # Если нужно отправлять в ЛС, нужно получить chat_id пользователя
        # await context.bot.send_message(chat_id=CHAT_ID_PUFFPLACE74, text=message, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")

async def show_warehouse_selection(query, action: str) -> None:
    """Показать выбор склада"""
    keyboard = [
        [InlineKeyboardButton("🏢 Склад Город", callback_data=f"warehouse_{action}_city")],
        [InlineKeyboardButton("🏭 Склад Таловка", callback_data=f"warehouse_{action}_talovka")],
    ]
    
    # Добавляем кнопку сброса только для @puffplace74 в меню продаж
    if action == "sales" and await check_reset_authorization(query):
        keyboard.append([InlineKeyboardButton("🔄 Сбросить все данные", callback_data="reset_data")])
    
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    action_text = "посмотреть наличие" if action == "view" else "регистрации продаж"
    await query.edit_message_text(
        f"Выберите склад для {action_text}:",
        reply_markup=reply_markup
    )

async def show_stock(query, warehouse: str) -> None:
    """Показать наличие товаров на складе"""
    stock_data = warehouse_manager.warehouse_city if warehouse == "city" else warehouse_manager.warehouse_talovka
    warehouse_name = "Город" if warehouse == "city" else "Таловка"
    
    message = f"📦 **Склад {warehouse_name}**\n\n"
    
    for product, quantity in stock_data.items():
        emoji = "🟢" if quantity > 0 else "🔴"
        message += f"{emoji} {product}: {quantity} шт.\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад к выбору склада", callback_data="back_to_warehouse_selection_view")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_products_for_sale(query, warehouse: str) -> None:
    """Показать товары для продажи"""
    stock_data = warehouse_manager.warehouse_city if warehouse == "city" else warehouse_manager.warehouse_talovka
    warehouse_name = "Город" if warehouse == "city" else "Таловка"
    
    message = f"💰 **Регистрация продаж - Склад {warehouse_name}**\n\nВыберите товар:\n"
    
    keyboard = []
    products = list(stock_data.keys())
    
    # Создаем кнопки для товаров (по 1 в ряд для лучшей читаемости)
    for i in range(len(products)):
        product = products[i]
        stock = stock_data[product]
        emoji = "🟢" if stock > 0 else "🔴"
        
        # Создаем понятное название для кнопки
        button_text = create_product_button_text(product, stock)
        
        button = InlineKeyboardButton(
            button_text, 
            callback_data=f"product_{warehouse}_{i}"
        )
        keyboard.append([button])
    
    keyboard.extend([
        [InlineKeyboardButton("🔙 Назад к выбору склада", callback_data="back_to_warehouse_selection_sales")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_main")]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

def create_product_button_text(product_name: str, stock: int) -> str:
    """Создает понятный текст для кнопки товара"""
    # Убираем лишние части названий для компактности
    short_name = product_name
    
    # Заменяем длинные названия брендов на сокращения
    replacements = {
        "Malasian x Protest - ": "MxP ",
        "Podonki Blood - ": "PB ",
        "Анархия V2 Strong ": "Анархия ",
        "Монархия - ": "Монархия ",
        "MPAK & ЧЁ NADO - ": "MPAK ",
        "Хаски на Аляске Hard - ": "Хаски ",
        "LOST MARY MO30000 - ": "LM ",
        "LOST MARY OS12000 ": "LM "
    }
    
    for old, new in replacements.items():
        short_name = short_name.replace(old, new)
    
    # Добавляем эмодзи наличия и количество
    emoji = "🟢" if stock > 0 else "🔴"
    
    # Ограничиваем длину и добавляем количество
    if len(short_name) > 30:
        short_name = short_name[:27] + "..."
    
    return f"{emoji} {short_name} ({stock} шт.)"

async def confirm_sale(query, warehouse: str, product_name: str) -> None:
    """Подтверждение продажи"""
    stock_data = warehouse_manager.warehouse_city if warehouse == "city" else warehouse_manager.warehouse_talovka
    warehouse_name = "Город" if warehouse == "city" else "Таловка"
    current_stock = stock_data[product_name]
    
    products = list(stock_data.keys())
    product_index = products.index(product_name)
    
    message = (f"💰 **Подтверждение продажи**\n\n"
               f"📦 Товар: {product_name}\n"
               f"🏢 Склад: {warehouse_name}\n"
               f"📊 Текущее наличие: {current_stock} шт.\n\n"
               f"Подтвердить продажу?")
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=f"confirm_{warehouse}_{product_index}_yes"),
            InlineKeyboardButton("❌ Нет", callback_data=f"confirm_{warehouse}_{product_index}_no")
        ],
        [InlineKeyboardButton("🔙 Назад к товарам", callback_data=f"warehouse_sales_{warehouse}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def check_authorization(query) -> bool:
    """Проверка авторизации пользователя для продаж"""
    user_username = f"@{query.from_user.username}" if query.from_user.username else None
    return user_username in AUTHORIZED_USERS

async def check_reset_authorization(query) -> bool:
    """Проверка авторизации пользователя для сброса данных"""
    user_username = f"@{query.from_user.username}" if query.from_user.username else None
    return user_username in RESET_USERS

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    await update.message.reply_text("Используйте кнопки меню для навигации")

def main() -> None:
    """Основная функция"""
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    application = Application.builder().token("8374095503:AAHdapIvuCdi4hjodFWvhz-OVvbEJ44jxdw").build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    print("Бот запущен...")
    print("Данные загружены из файла:", DATA_FILE)
    application.run_polling()

if __name__ == '__main__':
    main()
