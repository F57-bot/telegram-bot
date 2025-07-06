import logging
import random
from typing import Dict, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import uuid

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن ربات (از @BotFather دریافت کنید)
BOT_TOKEN = "7856939358:AAFys5p-cPWLxlkwYr8FWlata7PSpM39UVs"

# ذخیره پیام‌های مخفی (در حافظه - برای استفاده واقعی از پایگاه داده استفاده کنید)
secret_messages: Dict[str, Tuple[str, str]] = {}  # emoji: (message, password)

# وضعیت کاربران
user_states: Dict[int, str] = {}  # user_id: state
user_temp_data: Dict[int, dict] = {}  # user_id: temporary data

# لیست کامل ایموجی‌های تلگرام
AVAILABLE_EMOJIS = [
    # چهره‌ها و احساسات
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾",
    
    # ژست‌ها و بدن
    "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤌", "🤏", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", "👇", "☝️", "👍", "👎", "👊", "✊", "🤛", "🤜", "👏", "🙌", "👐", "🤲", "🤝", "🙏", "✍️", "💅", "🤳", "💪", "🦾", "🦿", "🦵", "🦶", "👂", "🦻", "👃", "🧠", "🫀", "🫁", "🦷", "🦴", "👀", "👁️", "👅", "👄", "💋", "🩸",
    
    # لباس و اکسسوری
    "👶", "🧒", "👦", "👧", "🧑", "👱", "👨", "🧔", "👩", "🧓", "👴", "👵", "🙍", "🙎", "🙅", "🙆", "💁", "🙋", "🧏", "🙇", "🤦", "🤷", "👮", "🕵️", "💂", "🥷", "👷", "🤴", "👸", "👳", "👲", "🧕", "🤵", "👰", "🤰", "🤱", "👼", "🎅", "🤶", "🦸", "🦹", "🧙", "🧚", "🧛", "🧜", "🧝", "🧞", "🧟", "💆", "💇", "🚶", "🧍", "🧎", "🏃", "💃", "🕺", "🕴️", "👯", "🧖", "🧗", "🤺", "🏇", "⛷️", "🏂", "🏌️", "🏄", "🚣", "🏊", "⛹️", "🏋️", "🚴", "🚵", "🤸", "🤼", "🤽", "🤾", "🤹", "🧘", "🛀", "🛌", "👭", "👫", "👬", "💏", "💑", "👪",
    
    # حیوانات
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮", "🐷", "🐽", "🐸", "🐵", "🙈", "🙉", "🙊", "🐒", "🐔", "🐧", "🐦", "🐤", "🐣", "🐥", "🦆", "🦅", "🦉", "🦇", "🐺", "🐗", "🐴", "🦄", "🐝", "🐛", "🦋", "🐌", "🐞", "🐜", "🦟", "🦗", "🕷️", "🕸️", "🦂", "🐢", "🐍", "🦎", "🦖", "🦕", "🐙", "🦑", "🦐", "🦞", "🦀", "🐡", "🐠", "🐟", "🐬", "🐳", "🐋", "🦈", "🐊", "🐅", "🐆", "🦓", "🦍", "🦧", "🐘", "🦛", "🦏", "🐪", "🐫", "🦒", "🦘", "🐃", "🐂", "🐄", "🐎", "🐖", "🐏", "🐑", "🦙", "🐐", "🦌", "🐕", "🐩", "🦮", "🐕‍🦺", "🐈", "🐈‍⬛", "🐓", "🦃", "🦚", "🦜", "🦢", "🦩", "🕊️", "🐇", "🦝", "🦨", "🦡", "🦦", "🦥", "🐁", "🐀", "🐿️", "🦔",
    
    # طبیعت
    "🌵", "🎄", "🌲", "🌳", "🌴", "🌱", "🌿", "☘️", "🍀", "🎍", "🎋", "🍃", "🍂", "🍁", "🍄", "🐚", "🌾", "💐", "🌷", "🌹", "🥀", "🌺", "🌸", "🌼", "🌻", "🌞", "🌝", "🌛", "🌜", "🌚", "🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔", "🌙", "🌎", "🌍", "🌏", "🪐", "💫", "⭐", "🌟", "✨", "⚡", "☄️", "💥", "🔥", "🌪️", "🌈", "☀️", "🌤️", "⛅", "🌦️", "🌧️", "⛈️", "🌩️", "🌨️", "❄️", "☃️", "⛄", "🌬️", "💨", "💧", "💦", "☔", "☂️", "🌊", "🌫️",
    
    # غذا و نوشیدنی
    "🍇", "🍈", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏", "🍐", "🍑", "🍒", "🍓", "🫐", "🥝", "🍅", "🫒", "🥥", "🥑", "🍆", "🥔", "🥕", "🌽", "🌶️", "🫑", "🥒", "🥬", "🥦", "🧄", "🧅", "🍄", "🥜", "🌰", "🍞", "🥐", "🥖", "🫓", "🥨", "🥯", "🥞", "🧇", "🧀", "🍖", "🍗", "🥩", "🥓", "🍔", "🍟", "🍕", "🌭", "🥪", "🌮", "🌯", "🫔", "🥙", "🧆", "🥚", "🍳", "🥘", "🍲", "🫕", "🥣", "🥗", "🍿", "🧈", "🧂", "🥫", "🍱", "🍘", "🍙", "🍚", "🍛", "🍜", "🍝", "🍠", "🍢", "🍣", "🍤", "🍥", "🥮", "🍡", "🥟", "🥠", "🥡", "🦀", "🦞", "🦐", "🦑", "🦪", "🍦", "🍧", "🍨", "🍩", "🍪", "🎂", "🍰", "🧁", "🥧", "🍫", "🍬", "🍭", "🍮", "🍯", "🍼", "🥛", "☕", "🫖", "🍵", "🍶", "🍾", "🍷", "🍸", "🍹", "🍺", "🍻", "🥂", "🥃", "🥤", "🧋", "🧃", "🧉", "🧊",
    
    # فعالیت‌ها
    "⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱", "🪀", "🏓", "🏸", "🏒", "🏑", "🥍", "🏏", "🪃", "🥅", "⛳", "🪁", "🏹", "🎣", "🤿", "🥊", "🥋", "🎽", "🛹", "🛷", "⛸️", "🥌", "🎿", "⛷️", "🏂", "🪂", "🏋️", "🤼", "🤸", "⛹️", "🤺", "🤾", "🏌️", "🏇", "🧘", "🏄", "🏊", "🤽", "🚣", "🧗", "🚵", "🚴", "🏆", "🥇", "🥈", "🥉", "🏅", "🎖️", "🏵️", "🎗️", "🎫", "🎟️", "🎪", "🤹", "🎭", "🩰", "🎨", "🎬", "🎤", "🎧", "🎼", "🎵", "🎶", "🎹", "🥁", "🎷", "🎺", "🎸", "🪕", "🎻", "🎲", "♟️", "🎯", "🎳", "🎮", "🕹️", "🎰", "🧩",
    
    # سفر و مکان
    "🚗", "🚕", "🚙", "🚌", "🚎", "🏎️", "🚓", "🚑", "🚒", "🚐", "🛻", "🚚", "🚛", "🚜", "🏍️", "🛵", "🚲", "🛴", "🛹", "🛼", "🚁", "🛸", "✈️", "🛫", "🛬", "🪂", "💺", "🚀", "�satellite️", "🚉", "🚊", "🚝", "🚞", "🚋", "🚃", "🚋", "🚞", "🚝", "🚄", "🚅", "🚈", "🚂", "🚆", "🚇", "🚊", "🚉", "🛤️", "🛣️", "🛑", "🚥", "🚦", "🚧", "⚓", "⛵", "🛶", "🚤", "🛳️", "⛴️", "🛥️", "🚢", "🏰", "🏯", "🏟️", "🎡", "🎢", "🎠", "⛲", "⛱️", "🏖️", "🏝️", "🏜️", "🌋", "⛰️", "🏔️", "🗻", "🏕️", "⛺", "🏠", "🏡", "🏘️", "🏚️", "🏗️", "🏭", "🏢", "🏬", "🏣", "🏤", "🏥", "🏦", "🏨", "🏪", "🏫", "🏩", "💒", "🏛️", "⛪", "🕌", "🕍", "🛕", "🕋", "⛩️", "🛤️", "🛣️", "🗾", "🎑", "🏞️", "🌅", "🌄", "🌠", "🎇", "🎆", "🌇", "🌆", "🏙️", "🌃", "🌌", "🌉", "🌁",
    
    # اشیاء
    "⌚", "📱", "📲", "💻", "⌨️", "🖥️", "🖨️", "🖱️", "🖲️", "🕹️", "🗜️", "💽", "💾", "💿", "📀", "📼", "📷", "📸", "📹", "🎥", "📽️", "🎞️", "📞", "☎️", "📟", "📠", "📺", "📻", "🎙️", "🎚️", "🎛️", "🧭", "⏱️", "⏲️", "⏰", "🕰️", "⌛", "⏳", "📡", "🔋", "🔌", "💡", "🔦", "🕯️", "🪔", "🧯", "🛢️", "💸", "💵", "💴", "💶", "💷", "💰", "💳", "💎", "⚖️", "🧰", "🔧", "🔨", "⚒️", "🛠️", "⛏️", "🔩", "⚙️", "🧱", "⛓️", "🧲", "🔫", "💣", "🧨", "🪓", "🔪", "🗡️", "⚔️", "🛡️", "🚬", "⚰️", "⚱️", "🏺", "🔮", "📿", "🧿", "💈", "⚗️", "🔭", "🔬", "🕳️", "🩹", "🩺", "💊", "💉", "🩸", "🧬", "🦠", "🧫", "🧪", "🌡️", "🧹", "🧺", "🧻", "🚽", "🚰", "🚿", "🛁", "🛀", "🧴", "🧷", "🧸", "🧵", "🪡", "🧶", "🪢", "👓", "🕶️", "🥽", "🥼", "🦺", "👔", "👕", "👖", "🧣", "🧤", "🧥", "🧦", "👗", "👘", "🥻", "🩱", "🩲", "🩳", "👙", "👚", "👛", "👜", "👝", "🛍️", "🎒", "👞", "👟", "🥾", "🥿", "👠", "👡", "🩴", "👢", "👑", "👒", "🎩", "🎓", "🧢", "⛑️", "📿", "💄", "💍", "💎", "🔇", "🔈", "🔉", "🔊", "📢", "📣", "📯", "🔔", "🔕", "🎼", "🎵", "🎶", "🎙️", "🎚️", "🎛️", "🎤", "🎧", "📻", "🎷", "🎸", "🎹", "🎺", "🎻", "🪕", "🥁", "📱", "📲", "☎️", "📞", "📟", "📠", "🔋", "🔌", "💻", "🖥️", "🖨️", "⌨️", "🖱️", "🖲️", "💽", "💾", "💿", "📀", "🧮", "🎥", "🎞️", "📽️", "🎬", "📺", "📷", "📸", "📹", "📼", "🔍", "🔎", "🕯️", "💡", "🔦", "🏮", "🪔", "📔", "📕", "📖", "📗", "📘", "📙", "📚", "📓", "📒", "📃", "📜", "📄", "📰", "🗞️", "📑", "🔖", "🏷️", "💰", "💴", "💵", "💶", "💷", "💸", "💳", "🧾", "💹", "✉️", "📧", "📨", "📩", "📤", "📥", "📦", "📫", "📪", "📬", "📭", "📮", "🗳️", "✏️", "✒️", "🖋️", "🖊️", "🖌️", "🖍️", "📝", "💼", "📁", "📂", "🗂️", "📅", "📆", "🗒️", "🗓️", "📇", "📈", "📉", "📊", "📋", "📌", "📍", "📎", "🖇️", "📏", "📐", "✂️", "🗃️", "🗄️", "🗑️", "🔒", "🔓", "🔏", "🔐", "🔑", "🗝️", "🔨", "🪓", "⛏️", "⚒️", "🛠️", "🗡️", "⚔️", "🔫", "🪃", "🏹", "🛡️", "🔧", "🔩", "⚙️", "🗜️", "⚖️", "🦯", "🔗", "⛓️", "🧰", "🧲", "⚗️", "🧪", "🧫", "🧬", "🔬", "🔭", "📡", "💉", "🩸", "💊", "🩹", "🩺", "🚪", "🛏️", "🛋️", "🪑", "🚽", "🚿", "🛁", "🪤", "🪒", "🧴", "🧷", "🧹", "🧺", "🧻", "🧼", "🧽", "🧯", "🛒", "🚬", "⚰️", "⚱️", "🗿", "🏧", "🚮", "🚰", "♿", "🚹", "🚺", "🚻", "🚼", "🚾", "🛂", "🛃", "🛄", "🛅", "⚠️", "🚸", "⛔", "🚫", "🚳", "🚭", "🚯", "🚱", "🚷", "📵", "🔞", "☢️", "☣️", "⬆️", "↗️", "➡️", "↘️", "⬇️", "↙️", "⬅️", "↖️", "↕️", "↔️", "↩️", "↪️", "⤴️", "⤵️", "🔃", "🔄", "🔙", "🔚", "🔛", "🔜", "🔝", "🛐", "⚛️", "🕉️", "✡️", "☸️", "☯️", "✝️", "☦️", "☪️", "☮️", "🕎", "🔯", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓", "⛎", "🔀", "🔁", "🔂", "▶️", "⏩", "⏭️", "⏯️", "◀️", "⏪", "⏮️", "🔼", "⏫", "🔽", "⏬", "⏸️", "⏹️", "⏺️", "⏏️", "🎦", "🔅", "🔆", "📶", "📳", "📴", "♀️", "♂️", "⚕️", "♾️", "♻️", "⚜️", "🔱", "📛", "🔰", "⭕", "✅", "☑️", "✔️", "✖️", "❌", "❎", "➕", "➖", "➗", "➰", "➿", "〽️", "✳️", "✴️", "❇️", "‼️", "⁉️", "❓", "❔", "❕", "❗", "〰️", "©️", "®️", "™️", "🔟", "🔠", "🔡", "🔢", "🔣", "🔤", "🅰️", "🆎", "🅱️", "🆑", "🆒", "🆓", "ℹ️", "🆔", "Ⓜ️", "🆕", "🆖", "🅾️", "🆗", "🅿️", "🆘", "🆙", "🆚", "🈁", "🈂️", "🈷️", "🈶", "🈯", "🉐", "🈹", "🈚", "🈲", "🉑", "🈸", "🈴", "🈳", "㊗️", "㊙️", "🈺", "🈵", "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛", "⬜", "◼️", "◻️", "◾", "◽", "▪️", "▫️", "🔶", "🔷", "🔸", "🔹", "🔺", "🔻", "💠", "🔘", "🔳", "🔲", "🏁", "🚩", "🎌", "🏴", "🏳️", "🏳️‍🌈", "🏳️‍⚧️", "🏴‍☠️"
]

# وضعیت‌های مختلف
STATES = {
    "WAITING_LANGUAGE": "waiting_language",
    "WAITING_MESSAGE": "waiting_message",
    "WAITING_PASSWORD": "waiting_password", 
    "WAITING_EMOJI": "waiting_emoji",
    "WAITING_DECODE_PASSWORD": "waiting_decode_password"
}

# پیام‌های چندزبانه
MESSAGES = {
    "fa": {
        "choose_language": """
🌐 **لطفاً زبان خود را انتخاب کنید:**

یکی از زبان‌های زیر را انتخاب کنید تا ادامه دهیم:
        """,
        "welcome": """
🔐 **ربات پیام مخفی** 🔐

سلام! من می‌تونم پیام‌های مخفی برات ایجاد کنم.

✨ **امکانات:**
• تبدیل پیام به ایموجی مخفی
• حفاظت با رمز عبور
• پیام‌های یک‌بار مصرف

یکی از گزینه‌های زیر رو انتخاب کن:
        """,
        "create_secret_prompt": """
📝 **ایجاد پیام مخفی**

لطفاً پیام یا متنی که می‌خواهید تبدیل به مخفی شود را بفرستید:

✍️ هر متنی که بخواهید می‌تونید بفرستید
🔤 حروف، اعداد، ایموجی همه قابل قبول است
        """,
        "decode_secret_prompt": """
🔍 **فهمیدن پیام مخفی**

لطفاً ایموجی‌های مخفی که می‌خواهید بدانید داخلشان چه هست را وارد کنید:

🎭 فقط ایموجی‌ها را بفرستید
📝 می‌تونید چندین ایموجی با هم بفرستید
        """,
        "help_text": """
ℹ️ **راهنمای ربات پیام مخفی**

**🔐 ایجاد پیام مخفی:**
1. روی دکمه "ایجاد پیام مخفی" کلیک کنید
2. پیام خود را بفرستید
3. رمز عبور را وارد کنید
4. 28 ایموجی مخفی دریافت کنید

**🔍 فهمیدن پیام مخفی:**
1. روی دکمه "فهمیدن پیام مخفی" کلیک کنید
2. ایموجی‌های مخفی را بفرستید
3. رمز عبور را وارد کنید
4. پیام اصلی را دریافت کنید

**⚠️ نکات مهم:**
• هر پیام فقط یک‌بار قابل دریافت است
• پس از دریافت، پیام حذف می‌شود
• رمز حساس به حروف بزرگ و کوچک است
• 28 ایموجی مختلف برای هر پیام تولید می‌شود
        """,
        "back_to_main": """
🔐 **ربات پیام مخفی** 🔐

یکی از گزینه‌های زیر رو انتخاب کن:
        """,
        "message_received": """
✅ پیام شما دریافت شد!\n\n
🔐 حالا رمز عبور را بفرستید:\n
• هر رمزی که بخواهید می‌تونید انتخاب کنید\n
• حروف، اعداد، علامت‌ها همه مجاز است\n
• رمز را به خاطر بسپارید!
        """,
        "password_empty": "❌ رمز عبور نمی‌تواند خالی باشد!",
        "secret_created": """
✅ **پیام مخفی شما ایجاد شد!**

🎭 **17 ایموجی مخفی (برای کپی):**
`{emoji_text}`

📋 **نحوه استفاده:**
• این 17 ایموجی را برای گیرنده بفرستید
• گیرنده باید روی "فهمیدن پیام مخفی" کلیک کند
• سپس این ایموجی‌ها و رمز `{password}` را وارد کند

💡 **راهنمای کپی:**
• روی متن بالا کلیک کنید تا کپی شود
• یا آن را انتخاب کرده و کپی کنید

⚠️ **توجه:** پیام پس از اولین دریافت حذف می‌شود!
        """,
        "emojis_received": """
✅ ایموجی‌ها دریافت شد!\n\n
🔐 حالا رمز عبور را بفرستید:\n
• رمز عبور مربوط به این پیام مخفی را وارد کنید\n
• دقیقاً همان رمزی که هنگام ایجاد پیام تعین شده
        """,
        "message_decoded": """
🔓 **پیام مخفی پیدا شد!**

💌 **پیام اصلی:**
{message}

✅ پیام با موفقیت دریافت شد و از سیستم حذف شد.
🗑️ دیگر قابل دریافت نیست.
        """,
        "message_not_found": """
❌ **پیام مخفی پیدا نشد!**

🔍 **احتمالات:**
• رمز عبور اشتباه است
• پیام قبلاً دریافت شده و حذف شده
• ایموجی‌های وارد شده صحیح نیست

💡 **راه حل:**
• رمز عبور را دوباره بررسی کنید
• مطمئن شوید ایموجی‌ها کامل هستند
        """,
        "invalid_command": "لطفاً از دکمه‌ها استفاده کنید یا /start را بفرستید.",
        "stats": """
📊 **آمار ربات:**

🔐 پیام‌های مخفی فعال: {active_messages}
👥 کاربران فعال: {active_users}
        """,
        "create_secret_button": "📝 ایجاد پیام مخفی",
        "decode_secret_button": "🔍 فهمیدن پیام مخفی",
        "help_button": "ℹ️ راهنما",
        "back_button": "🔙 بازگشت",
        "main_menu_button": "🏠 منوی اصلی"
    },
    "en": {
        "choose_language": """
🌐 **Please select your language:**

Choose one of the languages below to proceed:
        """,
        "welcome": """
🔐 **Secret Message Bot** 🔐

Hello! I can create secret messages for you.

✨ **Features:**
• Convert messages to secret emojis
• Password protection
• One-time-use messages

Select an option below:
        """,
        "create_secret_prompt": """
📝 **Create a Secret Message**

Please send the message or text you want to hide:

✍️ You can send any text you want
🔤 Letters, numbers, emojis are all accepted
        """,
        "decode_secret_prompt": """
🔍 **Decode a Secret Message**

Please enter the secret emojis you want to decode:

🎭 Send only the emojis
📝 You can send multiple emojis together
        """,
        "help_text": """
ℹ️ **Secret Message Bot Guide**

**🔐 Create a Secret Message:**
1. Click on "Create a Secret Message"
2. Send your message
3. Enter a password
4. Receive 28 secret emojis

**🔍 Decode a Secret Message:**
1. Click on "Decode a Secret Message"
2. Send the secret emojis
3. Enter the password
4. Receive the original message

**⚠️ Important Notes:**
• Each message can only be retrieved once
• After retrieval, the message is deleted
• Password is case-sensitive
• 28 unique emojis are generated for each message
        """,
        "back_to_main": """
🔐 **Secret Message Bot** 🔐

Select an option below:
        """,
        "message_received": """
✅ Your message has been received!\n\n
🔐 Now send a password:\n
• Choose any password you like\n
• Letters, numbers, symbols are all allowed\n
• Remember your password!
        """,
        "password_empty": "❌ The password cannot be empty!",
        "secret_created": """
✅ **Your secret message has been created!**

🎭 **17 Secret Emojis (for copying):**
`{emoji_text}`

📋 **How to use:**
• Send these 17 emojis to the recipient
• The recipient should click "Decode a Secret Message"
• Then enter these emojis and the password `{password}`

💡 **Copying Guide:**
• Click the text above to copy it
• Or select and copy it manually

⚠️ **Note:** The message will be deleted after the first retrieval!
        """,
        "emojis_received": """
✅ Emojis received!\n\n
🔐 Now send the password:\n
• Enter the password for this secret message\n
• Exactly the same password set when creating the message
        """,
        "message_decoded": """
🔓 **Secret Message Found!**

💌 **Original Message:**
{message}

✅ The message was successfully retrieved and deleted from the system.
🗑️ It is no longer retrievable.
        """,
        "message_not_found": """
❌ **Secret Message Not Found!**

🔍 **Possible Reasons:**
• The password is incorrect
• The message has already been retrieved and deleted
• The entered emojis are incorrect

💡 **Solution:**
• Double-check the password
• Ensure the emojis are complete
        """,
        "invalid_command": "Please use the buttons or send /start.",
        "stats": """
📊 **Bot Statistics:**

🔐 Active secret messages: {active_messages}
👥 Active users: {active_users}
        """,
        "create_secret_button": "📝 Create Secret Message",
        "decode_secret_button": "🔍 Decode Secret Message",
        "help_button": "ℹ️ Help",
        "back_button": "🔙 Back",
        "main_menu_button": "🏠 Main Menu"
    },
    "ar": {
        "choose_language": """
🌐 **يرجى اختيار لغتك:**

اختر إحدى اللغات أدناه للمتابعة:
        """,
        "welcome": """
🔐 **بوت الرسائل السرية** 🔐

مرحبًا! يمكنني إنشاء رسائل سرية لك.

✨ **الميزات:**
• تحويل الرسائل إلى إيموجي سري
• الحماية بكلمة مرور
• رسائل للاستخدام مرة واحدة

اختر أحد الخيارات أدناه:
        """,
        "create_secret_prompt": """
📝 **إنشاء رسالة سرية**

يرجى إرسال الرسالة أو النص الذي تريد إخفاءه:

✍️ يمكنك إرسال أي نص تريده
🔤 الحروف، الأرقام، الإيموجي، كلها مقبولة
        """,
        "decode_secret_prompt": """
🔍 **فك تشفير رسالة سرية**

يرجى إدخال الإيموجيات السرية التي تريد فك تشفيرها:

🎭 أرسل الإيموجيات فقط
📝 يمكنك إرسال عدة إيموجيات معًا
        """,
        "help_text": """
ℹ️ **دليل بوت الرسائل السرية**

**🔐 إنشاء رسالة سرية:**
1. انقر على "إنشاء رسالة سرية"
2. أرسل رسالتك
3. أدخل كلمة المرور
4. احصل على 28 إيموجي سري

**🔍 فك تشفير رسالة سرية:**
1. انقر على "فك تشفير رسالة سرية"
2. أرسل الإيموجيات السرية
3. أدخل كلمة المرور
4. احصل على الرسالة الأصلية

**⚠️ ملاحظات هامة:**
• يمكن استرجاع كل رسالة مرة واحدة فقط
• بعد الاسترجاع، يتم حذف الرسالة
• كلمة المرور حساسة لحالة الأحرف
• يتم إنشاء 28 إيموجي مختلف لكل رسالة
        """,
        "back_to_main": """
🔐 **بوت الرسائل السرية** 🔐

اختر أحد الخيارات أدناه:
        """,
        "message_received": """
✅ تم استلام رسالتك!\n\n
🔐 الآن أرسل كلمة المرور:\n
• اختر أي كلمة مرور تريدها\n
• الحروف، الأرقام، الرموز، كلها مسموح بها\n
• تذكر كلمة المرور الخاصة بك!
        """,
        "password_empty": "❌ كلمة المرور لا يمكن أن تكون فارغة!",
        "secret_created": """
✅ **تم إنشاء رسالتك السرية!**

🎭 **17 إيموجي سري (للنسخ):**
`{emoji_text}`

📋 **كيفية الاستخدام:**
• أرسل هذه الإيموجيات الـ 17 إلى المستلم
• يجب على المستلم النقر على "فك تشفير رسالة سرية"
• ثم إدخال هذه الإيموجيات وكلمة المرور `{password}`

💡 **دليل النسخ:**
• انقر على النص أعلاه لنسخه
• أو حدده وانسخه يدويًا

⚠️ **ملاحظة:** سيتم حذف الرسالة بعد الاسترجاع الأول!
        """,
        "emojis_received": """
✅ تم استلام الإيموجيات!\n\n
🔐 الآن أرسل كلمة المرور:\n
• أدخل كلمة المرور لهذه الرسالة السرية\n
• بالضبط نفس كلمة المرور التي تم تحديدها عند إنشاء الرسالة
        """,
        "message_decoded": """
🔓 **تم العثور على الرسالة السرية!**

💌 **الرسالة الأصلية:**
{message}

✅ تم استرجاع الرسالة بنجاح وحذفها من النظام.
🗑️ لم يعد من الممكن استرجاعها.
        """,
        "message_not_found": """
❌ **لم يتم العثور على الرسالة السرية!**

🔍 **الأسباب المحتملة:**
• كلمة المرور غير صحيحة
• تم استرجاع الرسالة وحذفها مسبقًا
• الإيموجيات المدخلة غير صحيحة

💡 **الحل:**
• تحقق من كلمة المرور مرة أخرى
• تأكد من اكتمال الإيموجيات
        """,
        "invalid_command": "يرجى استخدام الأزرار أو إرسال /start.",
        "stats": """
📊 **إحصائيات البوت:**

🔐 الرسائل السرية النشطة: {active_messages}
👥 المستخدمون النشطون: {active_users}
        """,
        "create_secret_button": "📝 إنشاء رسالة سرية",
        "decode_secret_button": "🔍 فك تشفير رسالة سرية",
        "help_button": "ℹ️ مساعدة",
        "back_button": "🔙 رجوع",
        "main_menu_button": "🏠 القائمة الرئيسية"
    },
    "ru": {
        "choose_language": """
🌐 **Пожалуйста, выберите язык:**

Выберите один из языков ниже, чтобы продолжить:
        """,
        "welcome": """
🔐 **Бот секретных сообщений** 🔐

Привет! Я могу создавать для тебя секретные сообщения.

✨ **Возможности:**
• Преобразование сообщений в секретные эмодзи
• Защита паролем
• Сообщения для одноразового использования

Выбери один из вариантов ниже:
        """,
        "create_secret_prompt": """
📝 **Создать секретное сообщение**

Пожалуйста, отправь сообщение или текст, который хочешь скрыть:

✍️ Ты можешь отправить любой текст
🔤 Буквы, цифры, эмодзи — всё подходит
        """,
        "decode_secret_prompt": """
🔍 **Расшифровать секретное сообщение**

Пожалуйста, введи секретные эмодзи, которые хочешь расшифровать:

🎭 Отправляй только эмодзи
📝 Можно отправить сразу несколько эмодзи
        """,
        "help_text": """
ℹ️ **Руководство по боту секретных сообщений**

**🔐 Создание секретного сообщения:**
1. Нажми на кнопку "Создать секретное сообщение"
2. Отправь свое сообщение
3. Введи пароль
4. Получи 28 секретных эмодзи

**🔍 Расшифровка секретного сообщения:**
1. Нажми на кнопку "Расшифровать секретное сообщение"
2. Отправь секретные эмодзи
3. Введи пароль
4. Получи исходное сообщение

**⚠️ Важные заметки:**
• Каждое сообщение можно получить только один раз
• После получения сообщение удаляется
• Пароль чувствителен к регистру
• Для каждого сообщения создается 28 уникальных эмодзи
        """,
        "back_to_main": """
🔐 **Бот секретных сообщений** 🔐

Выбери один из вариантов ниже:
        """,
        "message_received": """
✅ Твое сообщение получено!\n\n
🔐 Теперь отправь пароль:\n
• Выбери любой пароль\n
• Буквы, цифры, символы — всё разрешено\n
• Запомни свой пароль!
        """,
        "password_empty": "❌ Пароль не может быть пустым!",
        "secret_created": """
✅ **Твое секретное сообщение создано!**

🎭 **17 секретных эмодзи (для копирования):**
`{emoji_text}`

📋 **Как использовать:**
• Отправь эти 17 эмодзи получателю
• Получатель должен нажать "Расшифровать секретное сообщение"
• Затем ввести эти эмодзи и пароль `{password}`

💡 **Инструкция по копированию:**
• Нажми на текст выше, чтобы скопировать
• Или выбери и скопируй вручную

⚠️ **Внимание:** Сообщение будет удалено после первого получения!
        """,
        "emojis_received": """
✅ Эмодзи получены!\n\n
🔐 Теперь отправь пароль:\n
• Введи пароль для этого секретного сообщения\n
• Точно такой же пароль, который был задан при создании сообщения
        """,
        "message_decoded": """
🔓 **Секретное сообщение найдено!**

💌 **Исходное сообщение:**
{message}

✅ Сообщение успешно получено и удалено из системы.
🗑️ Его больше нельзя получить.
        """,
        "message_not_found": """
❌ **Секретное сообщение не найдено!**

🔍 **Возможные причины:**
• Пароль неверный
• Сообщение уже было получено и удалено
• Введенные эмодзи неверные

💡 **Решение:**
• Проверь пароль еще раз
• Убедись, что эмодзи введены полностью
        """,
        "invalid_command": "Пожалуйста, используй кнопки или отправь /start.",
        "stats": """
📊 **Статистика бота:**

🔐 Активные секретные сообщения: {active_messages}
👥 Активные пользователи: {active_users}
        """,
        "create_secret_button": "📝 Создать секретное сообщение",
        "decode_secret_button": "🔍 Расшифровать секретное сообщение",
        "help_button": "ℹ️ Помощь",
        "back_button": "🔙 Назад",
        "main_menu_button": "🏠 Главное меню"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پیام خوش‌آمدگویی با انتخاب زبان"""
    user_id = update.effective_user.id
    
    # پاک کردن وضعیت قبلی کاربر
    user_states.pop(user_id, None)
    user_temp_data.pop(user_id, None)
    
    # تنظیم حالت انتخاب زبان
    user_states[user_id] = STATES["WAITING_LANGUAGE"]
    user_temp_data[user_id] = {}
    
    keyboard = [
        [InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa")],
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("العربية 🇸🇦", callback_data="lang_ar")],
        [InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        MESSAGES["fa"]["choose_language"],  # Default to Persian for initial prompt
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پردازش کلیک روی دکمه‌ها"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_temp_data[user_id]["language"] = lang
        await show_main_menu(query, user_id, lang)
    elif data == "create_secret":
        await start_create_secret(query, user_id)
    elif data == "decode_secret":
        await start_decode_secret(query, user_id)
    elif data == "help":
        await show_help(query, user_id)
    elif data == "back_to_main":
        await back_to_main(query, user_id)

async def show_main_menu(query, user_id: int, lang: str) -> None:
    """نمایش منوی اصلی با زبان انتخاب‌شده"""
    user_states.pop(user_id, None)  # پاک کردن حالت انتخاب زبان
    
    keyboard = [
        [InlineKeyboardButton(MESSAGES[lang]["create_secret_button"], callback_data="create_secret")],
        [InlineKeyboardButton(MESSAGES[lang]["decode_secret_button"], callback_data="decode_secret")],
        [InlineKeyboardButton(MESSAGES[lang]["help_button"], callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES[lang]["welcome"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def start_create_secret(query, user_id: int) -> None:
    """شروع فرایند ایجاد پیام مخفی"""
    lang = user_temp_data[user_id].get("language", "fa")
    user_states[user_id] = STATES["WAITING_MESSAGE"]
    
    keyboard = [[InlineKeyboardButton(MESSAGES[lang]["back_button"], callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES[lang]["create_secret_prompt"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def start_decode_secret(query, user_id: int) -> None:
    """شروع فرایند فهمیدن پیام مخفی"""
    lang = user_temp_data[user_id].get("language", "fa")
    user_states[user_id] = STATES["WAITING_EMOJI"]
    
    keyboard = [[InlineKeyboardButton(MESSAGES[lang]["back_button"], callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES[lang]["decode_secret_prompt"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def show_help(query, user_id: int) -> None:
    """نمایش راهنما"""
    lang = user_temp_data[user_id].get("language", "fa")
    keyboard = [[InlineKeyboardButton(MESSAGES[lang]["back_button"], callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES[lang]["help_text"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def back_to_main(query, user_id: int) -> None:
    """بازگشت به منوی اصلی"""
    lang = user_temp_data[user_id].get("language", "fa")
    
    # پاک کردن وضعیت کاربر
    user_states.pop(user_id, None)
    
    keyboard = [
        [InlineKeyboardButton(MESSAGES[lang]["create_secret_button"], callback_data="create_secret")],
        [InlineKeyboardButton(MESSAGES[lang]["decode_secret_button"], callback_data="decode_secret")],
        [InlineKeyboardButton(MESSAGES[lang]["help_button"], callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        MESSAGES[lang]["back_to_main"],
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پردازش پیام‌های کاربر"""
    user_id = update.effective_user.id
    message_text = update.message.text
    lang = user_temp_data.get(user_id, {}).get("language", "fa")
    
    if user_id not in user_states:
        # کاربر در حالت عادی است
        await update.message.reply_text(
            MESSAGES[lang]["invalid_command"],
            parse_mode='Markdown'
        )
        return
    
    state = user_states[user_id]
    
    if state == STATES["WAITING_LANGUAGE"]:
        await update.message.reply_text(
            MESSAGES[lang]["choose_language"],
            parse_mode='Markdown'
        )
    elif state == STATES["WAITING_MESSAGE"]:
        await handle_message_input(update, user_id, message_text)
    elif state == STATES["WAITING_PASSWORD"]:
        await handle_password_input(update, user_id, message_text)
    elif state == STATES["WAITING_EMOJI"]:
        await handle_emoji_input(update, user_id, message_text)
    elif state == STATES["WAITING_DECODE_PASSWORD"]:
        await handle_decode_password_input(update, user_id, message_text)

async def handle_message_input(update: Update, user_id: int, message_text: str) -> None:
    """پردازش پیام کاربر برای ایجاد پیام مخفی"""
    lang = user_temp_data[user_id].get("language", "fa")
    user_temp_data[user_id]["message"] = message_text
    user_states[user_id] = STATES["WAITING_PASSWORD"]
    
    await update.message.reply_text(
        MESSAGES[lang]["message_received"],
        parse_mode='Markdown'
    )

async def handle_password_input(update: Update, user_id: int, password: str) -> None:
    """پردازش رمز عبور و ایجاد پیام مخفی"""
    lang = user_temp_data[user_id].get("language", "fa")
    
    if len(password.strip()) == 0:
        await update.message.reply_text(
            MESSAGES[lang]["password_empty"],
            parse_mode='Markdown'
        )
        return
    
    message = user_temp_data[user_id]["message"]
    
    # انتخاب 17 ایموجی تصادفی
    selected_emojis = random.sample(AVAILABLE_EMOJIS, 17)
    
    # انتخاب یکی از آنها برای ذخیره پیام
    secret_emoji = random.choice(selected_emojis)
    
    # ذخیره پیام
    secret_messages[secret_emoji] = (message, password)
    
    # ایجاد متن ایموجی‌ها (قابل کپی)
    emoji_text = "".join(selected_emojis)  # بدون فاصله برای کپی آسان‌تر
    emoji_text_display = " ".join(selected_emojis)  # با فاصله برای نمایش بهتر
    
    # پاک کردن وضعیت کاربر
    user_states.pop(user_id, None)
    user_temp_data.pop(user_id, None)
    
    keyboard = [[InlineKeyboardButton(MESSAGES[lang]["main_menu_button"], callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    response_text = MESSAGES[lang]["secret_created"].format(emoji_text=emoji_text, password=password)
    
    await update.message.reply_text(
        response_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_emoji_input(update: Update, user_id: int, emoji_text: str) -> None:
    """پردازش ایموجی‌های وارد شده"""
    lang = user_temp_data[user_id].get("language", "fa")
    user_temp_data[user_id]["emojis"] = emoji_text
    user_states[user_id] = STATES["WAITING_DECODE_PASSWORD"]
    
    await update.message.reply_text(
        MESSAGES[lang]["emojis_received"],
        parse_mode='Markdown'
    )

async def handle_decode_password_input(update: Update, user_id: int, password: str) -> None:
    """پردازش رمز عبور و بازیابی پیام مخفی"""
    lang = user_temp_data[user_id].get("language", "fa")
    emoji_text = user_temp_data[user_id]["emojis"]
    
    # جستجو در بین ایموجی‌های موجود
    found_message = None
    found_emoji = None
    
    for emoji in emoji_text:
        if emoji in secret_messages:
            stored_message, stored_password = secret_messages[emoji]
            if stored_password == password:
                found_message = stored_message
                found_emoji = emoji
                break
    
    # پاک کردن وضعیت کاربر
    user_states.pop(user_id, None)
    user_temp_data.pop(user_id, None)
    
    keyboard = [[InlineKeyboardButton(MESSAGES[lang]["main_menu_button"], callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if found_message:
        # حذف پیام از حافظه
        del secret_messages[found_emoji]
        
        response_text = MESSAGES[lang]["message_decoded"].format(message=found_message)
    else:
        response_text = MESSAGES[lang]["message_not_found"]
    
    await update.message.reply_text(
        response_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """نمایش آمار ربات"""
    user_id = update.effective_user.id
    lang = user_temp_data.get(user_id, {}).get("language", "fa")
    active_messages = len(secret_messages)
    active_users = len(user_states)
    
    await update.message.reply_text(
        MESSAGES[lang]["stats"].format(active_messages=active_messages, active_users=active_users),
        parse_mode='Markdown'
    )

def main() -> None:
    """اجرای ربات"""
    # ایجاد اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # اجرای ربات
    print("🤖 Secret Message Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()