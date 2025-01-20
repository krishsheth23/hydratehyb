from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from telegram import ReplyKeyboardMarkup

# Define states for the conversation
WEIGHT, REMINDER, MENU = range(3)

# This will hold user's information
user_data = {}

async def start(update: Update, context: CallbackContext) -> int:
    user_data[update.message.chat_id] = {}
    await update.message.reply_text("Welcome to HydrateHub! Please enter your weight (in kg):")
    return WEIGHT

async def get_weight(update: Update, context: CallbackContext) -> int:
    weight = update.message.text.strip()

    try:
        weight = float(weight)
        if weight <= 0:
            await update.message.reply_text("Please enter a valid weight greater than 0.")
            return WEIGHT
    except ValueError:
        await update.message.reply_text("That's not a valid number. Please enter a valid weight.")
        return WEIGHT

    user_data[update.message.chat_id]['weight'] = weight
    daily_goal = weight * 30  # Calculate daily goal based on weight

    user_data[update.message.chat_id]['daily_goal'] = daily_goal
    await update.message.reply_text(f"Your goal is {daily_goal} ml. Now, let's set your reminder time.")

    keyboard = [
        ["30 minutes", "1 hour", "2 hours"],
        ["Cancel"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("How often would you like to be reminded?", reply_markup=reply_markup)
    return REMINDER

async def set_reminder(update: Update, context: CallbackContext) -> int:
    reminder_time = update.message.text.strip().lower()

    valid_times = ["30 minutes", "1 hour", "2 hours"]

    if reminder_time in valid_times:
        user_data[update.message.chat_id]['reminder'] = reminder_time
        await update.message.reply_text(f"Reminder set for every {reminder_time}.")

        keyboard = [["Log Water", "Change Goal", "Change Time"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            f"Your goal is {user_data[update.message.chat_id]['daily_goal']} ml. You have logged 0 ml.",
            reply_markup=reply_markup
        )
        return MENU
    else:
        await update.message.reply_text("Please choose a valid reminder time.")
        return REMINDER

async def log_water(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("How much water did you drink? Enter the amount in ml.")
    return ConversationHandler.END

async def change_goal(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Please enter your new weight to adjust the goal:")
    return WEIGHT

async def change_time(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Please select a new reminder time.")
    return REMINDER

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Goodbye!")
    return ConversationHandler.END

def main():
    # Replace "YOUR_BOT_TOKEN" with your actual bot token
    application = Application.builder().token("Token").build()

    # Define the conversation handler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
            REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_reminder)],
            MENU: [
                MessageHandler(filters.TEXT & filters.Regex("Log Water"), log_water),
                MessageHandler(filters.TEXT & filters.Regex("Change Goal"), change_goal),
                MessageHandler(filters.TEXT & filters.Regex("Change Time"), change_time),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add the handler to the application
    application.add_handler(conversation_handler)

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
