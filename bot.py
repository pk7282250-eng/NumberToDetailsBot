import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from random import randint

# ====== YOUR TOKENS - EDIT THESE ======
TELEGRAM_BOT_TOKEN = "8075721450:AAEUX4daCZspepdX0PLNHvBkKMAv_1FRsUc"
LEAKOSINT_API_TOKEN = "5889016144:zuh2dsTH"  # The token for the leaky API
LEAKOSINT_API_URL = "https://leakosintapi.com/"

# ====== FUNCTION TO QUERY THE LEAKED DATABASE ======
def search_leaked_data(query):
    """Sends a request to the leakosint API and returns the parsed JSON response."""
    payload = {
        "token": LEAKOSINT_API_TOKEN,
        "request": query,
        "limit": 100,
        "lang": "en",
        "type": "json"
    }
    try:
        response = requests.post(LEAKOSINT_API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API Request failed: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse API response: {str(e)}"}

# ====== FUNCTION TO FORMAT THE RESULT LIKE YOUR SCREENSHOT ======
def format_phone_result(api_data):
    """Formats the API's JSON response into the 'Mobile Info Result' style from your screenshot."""
    if "error" in api_data:
        return f"❌ Error: {api_data['error']}"

    formatted_text = "Mobile Info Result:\n\n"
    
    # Check if the API returns data in the expected structure
    if 'data' in api_data and isinstance(api_data['data'], list):
        for entry in api_data['data']:
            formatted_text += f"Name: {entry.get('name', 'N/A')}\n"
            formatted_text += f"Father's Name: {entry.get('fname', 'N/A')}\n"
            formatted_text += f"Address: {entry.get('address', 'N/A')}\n"
            formatted_text += f"Alt Number: {entry.get('alt', 'N/A')}\n"
            formatted_text += f"Circle: {entry.get('circle', 'N/A')}\n"
            formatted_text += f"Email: {entry.get('email', 'N/A')}\n"
            formatted_text += "─" * 20 + "\n\n"
    else:
        # If the structure is different, just show the raw JSON
        formatted_text += "Received unexpected data format:\n"
        formatted_text += json.dumps(api_data, indent=2, ensure_ascii=False)
    
    # Trim the message if it's too long for Telegram
    if len(formatted_text) > 4000:
        formatted_text = formatted_text[:4000] + "\n\n... (output truncated) ..."
    
    return formatted_text

# ====== TELEGRAM BOT HANDLERS ======
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    welcome_text = """
    🔍 *Number To Details Bot*
    
    I can search for information associated with a phone number.
    
    *How to use:*
    Just send me a phone number like this:
    `9350179348`
    
    Or use the command:
    `/num 9350179348`
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /num command."""
    if not context.args:
        await update.message.reply_text("Please provide a phone number. Usage: `/num 9350179348`", parse_mode='Markdown')
        return
        
    phone_number = context.args[0]
    # Send a "searching" message
    searching_msg = await update.message.reply_text("Searching, please wait...")
    
    # Call the dangerous API
    api_data = search_leaked_data(phone_number)
    
    # Format the result
    result_text = format_phone_result(api_data)
    
    # Edit the original "searching" message with the results
    await searching_msg.edit_text(result_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles any text message that isn't a command. Treats it as a phone number."""
    if update.message.text.startswith('/'):
        return  # Ignore commands, they have their own handlers
    
    phone_number = update.message.text.strip()
    # Basic validation: check if it looks like a number
    if not phone_number.isdigit() or len(phone_number) < 10:
        await update.message.reply_text("Please send a valid phone number (digits only, at least 10 characters).")
        return
        
    searching_msg = await update.message.reply_text("Searching, please wait...")
    api_data = search_leaked_data(phone_number)
    result_text = format_phone_result(api_data)
    await searching_msg.edit_text(result_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logs errors."""
    print(f"Update {update} caused error {context.error}")

# ====== MAIN BOT SETUP ======
def main():
    """Start the bot."""
    print("Starting Number To Details Bot...")
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("num", num_command))
    application.add_handler(CommandHandler("help", start_command)) # Reuse start for help
    application.add_handler(MessageHandler(None, handle_message)) # Handle all text messages
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    print("Bot is now running. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
