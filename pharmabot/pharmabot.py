# from telegram import Update, Bot
# from telegram.ext import Updater, CommandHandler, CallbackContext
# from geopy.distance import geodesic
# import sqlite3
# import telegram

# #db = sqlite3.connect("./farmacie.db")

# #with open("token.txt", "r") as f:
# #    TOKEN = f.read()
# #    print(TOKEN)

# #def main():
# #    app = ApplicationBuilder().token(TOKEN).build()
# #    app.add_handler(CommandHandler("start", start))
# #    app.add_handler(CommandHandler("FarmaciaVicina", get_nearest_pharma))

# #async def hello_funct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #    hello_var = update.effective_user.first_name
# #    await update.message.reply_text("Hello %s" % hello_var)

# #async def start_funct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #        hello_var = update.effective_user.first_name
# #        await update.message.reply_text("Ciao %s! Sono PharmaBot, ho la funzione di aiutarti a scegliere la farmacia ideale e più conveniente per te! Clicca uno dei tasti qui sotto per selezionare una funzione" %hello_var)


# def main() -> None:
#     def main() -> None:
#         TOKEN = "5643203403:AAEjSi-VlOLREODuq60Tm19wyjPmhHBpvjs"
#         bot = telegram.Bot(token=TOKEN)
#         bot._request.required_connection_pool_size = 16  # Set connection pool size directly on the bot instance
#         updater = Updater(bot=bot)
#         dispatcher = updater.dispatcher

#         start_handler = CommandHandler("start", start)
#         get_nearest_pharma_handler = CommandHandler("FarmaciaVicina", get_nearest_pharma)

#         dispatcher.add_handler(start_handler)
#         dispatcher.add_handler(get_nearest_pharma_handler)

#         updater.start_polling()
#         updater.idle()

# def start(update: Update, context: CallbackContext) -> None:
#     context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter your address.")

# def get_nearest_pharma(update: Update, context: CallbackContext) -> None:
#     try:
#         user_address = update.message.text

#         # Retrieve pharmacy addresses from the database
#         pharmacy_addresses = get_pharmacy_addresses()

#         # Calculate distances between user's address and each pharmacy
#         distances = []
#         for pharmacy_address in pharmacy_addresses:
#             distance = geodesic(user_address, pharmacy_address).kilometers
#             distances.append(distance)

#         if distances:
#             min_distance = min(distances)
#             nearest_pharmacy_index = distances.index(min_distance)
#             nearest_pharmacy = pharmacy_addresses[nearest_pharmacy_index]
#             update.message.reply_text(f"Nearest pharmacy address: {nearest_pharmacy}")
#         else:
#             update.message.reply_text("No nearby pharmacies found.")
#     except ValueError:
#         update.message.reply_text("Invalid address. Please try again.")
#     except Exception as e:
#         update.message.reply_text("An error occurred. Please try again later.")

# def get_pharmacy_addresses() -> list[str]:
#     conn = sqlite3.connect("farmacie.db")
#     cursor = conn.cursor()

#     # Assuming you have a table named 'pharmacies' with an 'address' column
#     cursor.execute("SELECT Indirizzo FROM farmacie")
#     rows = cursor.fetchall()

#     # Extract the addresses from the rows
#     pharmacy_addresses = [row[0] for row in rows]

#     conn.close()

#     return pharmacy_addresses



# if __name__ == '__main__':
#     main()

import sqlite3
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = '5643203403:AAEjSi-VlOLREODuq60Tm19wyjPmhHBpvjs'

database_name = "farmacie.db"

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I will find the closest pharmacy to your location.")

def get_user_location(update, context):
    user_id = update.effective_user.id

    
    user = context.bot.get_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
    user_location = user.location

    latitude = user_location.latitude
    longitude = user_location.longitude

    return latitude, longitude

def find_closest_pharmacy(latitude, longitude):
    user_coordinates = (latitude, longitude)
    geolocator = Nominatim(user_agent="my_bot")

    closest_pharmacy = None
    closest_address = None
    closest_distance = float('inf')

    
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    
    cursor.execute("SELECT Indirizzo FROM sqlite_master")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]

        
        cursor.execute(f"SELECT Nome, Indirizzo FROM {table_name}")
        rows = cursor.fetchall()

        for row in rows:
            pharmacy_name = row[0]
            pharmacy_address = row[1]
            location = geolocator.geocode(pharmacy_address)

            if location is not None:
                pharmacy_coordinates = (location.latitude, location.longitude)
                distance = geodesic(user_coordinates, pharmacy_coordinates).meters

                if distance < closest_distance:
                    closest_pharmacy = pharmacy_name
                    closest_address = pharmacy_address
                    closest_distance = distance

    # Close the database connection
    cursor.close()
    conn.close()

    if closest_pharmacy:
        return f"The closest pharmacy is:\n\nName: {closest_pharmacy}\nAddress: {closest_address}"
    else:
        return "No pharmacy found."

def handle_location(update, context):
    latitude, longitude = get_user_location(update, context)

    closest_pharmacy_message = find_closest_pharmacy(latitude, longitude)
    context.bot.send_message(chat_id=update.effective_chat.id, text=closest_pharmacy_message)

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    location_handler = MessageHandler(Filters.location, handle_location)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(location_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()





