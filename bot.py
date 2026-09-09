import os
import yt_dlp
from ddgs import DDGS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = '8726019832:AAG706rIHfWhFLQDkXM8fWVx7sKEduRqFe0'

def build_search_keyboard(entries, page=0, page_size=10):
    start_idx = page * page_size
    end_idx = start_idx + page_size
    page_entries = entries[start_idx:end_idx]

    keyboard = []
    for entry in page_entries:
        title = entry.get('title', 'Unknown Title')
        video_id = entry.get('id')
        if not video_id:
            continue
        display_title = title[:40] + "..." if len(title) > 40 else title
        keyboard.append([InlineKeyboardButton(display_title, callback_data=f"DL:{video_id}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ ယခင်", callback_data=f"NAV:{page-1}"))
    if end_idx < len(entries):
        nav_buttons.append(InlineKeyboardButton("နောက်ထပ် ➡️", callback_data=f"NAV:{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! အဆိုတော်နာမည် သို့မဟုတ် သီချင်းခေါင်းစဉ်ကို ရိုက်ပို့ပေးပါ။")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    status_msg = await update.message.reply_text("သီချင်းများ ရှာဖွေနေပါသည်... ခဏစောင့်ပါ။")

    try:
        results = []
        # ddgs မူရင်း search ဖြင့် YouTube ဗီဒီယိုများ ရှာဖွေခြင်း
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(f"{query} song site:youtube.com", max_results=20))
            for r in ddg_results:
                url = r.get('href', '') or r.get('link', '')
                title = r.get('title', 'YouTube Video')
                if 'watch?v=' in url:
                    v_id = url.split('watch?v=')[1].split('&')[0]
                    # YouTube Title ထဲမှ - YouTube စာတန်းအား ဖယ်ထုတ်ခြင်း
                    clean_title = title.replace('- YouTube', '').strip()
                    results.append({'id': v_id, 'title': clean_title})

        if not results:
            await status_msg.edit_text("သီချင်း ရှာမတွေ့ပါ။ စာလုံးပေါင်း ပြန်စစ်ပြီး ထပ်မံရိုက်ပို့ပေးပါ။")
            return

        context.user_data['search_entries'] = results
        reply_markup = build_search_keyboard(results, page=0)
        await status_msg.edit_text("တွေ့ရှိထားသော သီချင်းများ (နားထောင်ချင်သည့် သီချင်းကို နှိပ်ပါ):", reply_markup=reply_markup)

    except Exception as e:
        await status_msg.edit_text(f"အမှားဖြစ်ပွားရသည့် အကြောင်းအရင်း: {str(e)[:100]}")
        print(f"Search Error: {e}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("NAV:"):
        page = int(data.split(":")[1])
        entries = context.user_data.get('search_entries', [])
        if entries:
            reply_markup = build_search_keyboard(entries, page=page)
            await query.edit_message_text("တွေ့ရှိထားသော သီချင်းများ (နားထောင်ချင်သည့် သီချင်းကို နှိပ်ပါ):", reply_markup=reply_markup)
        return

    if data.startswith("DL:"):
        video_id = data.split(":")[1]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        await query.edit_message_text("သီချင်းကို ဒေါင်းလုဒ်ဆွဲနေပါသည်... ခဏစောင့်ပါ။")

        ydl_opts = {
            'format': 'ba[ext=m4a]/ba[ext=webm]/ba',
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'nocheckcertificate': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'Audio')

            with open(filename, 'rb') as audio_file:
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=audio_file, title=title)

            if os.path.exists(filename):
                os.remove(filename)

            await query.delete_message()

        except Exception as e:
            await query.edit_message_text("ဒေါင်းလုဒ်ဆွဲ၍ မရပါ။ အခြားသီချင်းတစ်ပုဒ် စမ်းကြည့်ပါ။")
            print(f"Download Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).connect_timeout(60.0).read_timeout(60.0).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()import os
import yt_dlp
from ddgs import DDGS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = '8726019832:AAG706rIHfWhFLQDkXM8fWVx7sKEduRqFe0'

def build_search_keyboard(entries, page=0, page_size=10):
    start_idx = page * page_size
    end_idx = start_idx + page_size
    page_entries = entries[start_idx:end_idx]

    keyboard = []
    for entry in page_entries:
        title = entry.get('title', 'Unknown Title')
        video_id = entry.get('id')
        if not video_id:
            continue
        display_title = title[:40] + "..." if len(title) > 40 else title
        keyboard.append([InlineKeyboardButton(display_title, callback_data=f"DL:{video_id}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ ယခင်", callback_data=f"NAV:{page-1}"))
    if end_idx < len(entries):
        nav_buttons.append(InlineKeyboardButton("နောက်ထပ် ➡️", callback_data=f"NAV:{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! အဆိုတော်နာမည် သို့မဟုတ် သီချင်းခေါင်းစဉ်ကို ရိုက်ပို့ပေးပါ။")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    status_msg = await update.message.reply_text("သီချင်းများ ရှာဖွေနေပါသည်... ခဏစောင့်ပါ။")

    try:
        results = []
        # ddgs မူရင်း search ဖြင့် YouTube ဗီဒီယိုများ ရှာဖွေခြင်း
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(f"{query} song site:youtube.com", max_results=20))
            for r in ddg_results:
                url = r.get('href', '') or r.get('link', '')
                title = r.get('title', 'YouTube Video')
                if 'watch?v=' in url:
                    v_id = url.split('watch?v=')[1].split('&')[0]
                    # YouTube Title ထဲမှ - YouTube စာတန်းအား ဖယ်ထုတ်ခြင်း
                    clean_title = title.replace('- YouTube', '').strip()
                    results.append({'id': v_id, 'title': clean_title})

        if not results:
            await status_msg.edit_text("သီချင်း ရှာမတွေ့ပါ။ စာလုံးပေါင်း ပြန်စစ်ပြီး ထပ်မံရိုက်ပို့ပေးပါ။")
            return

        context.user_data['search_entries'] = results
        reply_markup = build_search_keyboard(results, page=0)
        await status_msg.edit_text("တွေ့ရှိထားသော သီချင်းများ (နားထောင်ချင်သည့် သီချင်းကို နှိပ်ပါ):", reply_markup=reply_markup)

    except Exception as e:
        await status_msg.edit_text(f"အမှားဖြစ်ပွားရသည့် အကြောင်းအရင်း: {str(e)[:100]}")
        print(f"Search Error: {e}")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("NAV:"):
        page = int(data.split(":")[1])
        entries = context.user_data.get('search_entries', [])
        if entries:
            reply_markup = build_search_keyboard(entries, page=page)
            await query.edit_message_text("တွေ့ရှိထားသော သီချင်းများ (နားထောင်ချင်သည့် သီချင်းကို နှိပ်ပါ):", reply_markup=reply_markup)
        return

    if data.startswith("DL:"):
        video_id = data.split(":")[1]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        await query.edit_message_text("သီချင်းကို ဒေါင်းလုဒ်ဆွဲနေပါသည်... ခဏစောင့်ပါ။")

        ydl_opts = {
            'format': 'ba[ext=m4a]/ba[ext=webm]/ba',
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'nocheckcertificate': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'Audio')

            with open(filename, 'rb') as audio_file:
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=audio_file, title=title)

            if os.path.exists(filename):
                os.remove(filename)

            await query.delete_message()

        except Exception as e:
            await query.edit_message_text("ဒေါင်းလုဒ်ဆွဲ၍ မရပါ။ အခြားသီချင်းတစ်ပုဒ် စမ်းကြည့်ပါ။")
            print(f"Download Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).connect_timeout(60.0).read_timeout(60.0).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()
