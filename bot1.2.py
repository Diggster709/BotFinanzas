from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext, ConversationHandler
)

# Estados para el manejador de conversación
SET_SUELDO, GASTO, REINICIAR = range(3)

# Diccionario para almacenar la información del usuario
users_data = {}

# Comando /start para dar la bienvenida al usuario y mostrar los botones
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('¡Hola! Bienvenido al bot de seguimiento de salario y gastos. Selecciona una opción:', reply_markup=start_keyboard())

# Manejar las respuestas de los botones
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'set_sueldo':
        await query.edit_message_text('Por favor, ingresa tu sueldo quincenal:')
        return SET_SUELDO
    elif query.data == 'gasto':
        await query.edit_message_text('Por favor, ingresa el gasto:')
        return GASTO
    elif query.data == 'saldo':
        user_id = query.from_user.id
        if user_id in users_data:
            saldo_actual = users_data[user_id]['saldo']
            await query.edit_message_text(f'Tu saldo actual es {saldo_actual}.', reply_markup=start_keyboard())
        else:
            await query.edit_message_text('Primero ingresa tu sueldo quincenal usando /set_sueldo.', reply_markup=start_keyboard())
        return ConversationHandler.END
    elif query.data == 'reiniciar':
        await query.edit_message_text('Por favor, ingresa tu nuevo sueldo quincenal:')
        return REINICIAR

# Manejar la entrada de sueldo quincenal
async def set_sueldo(update: Update, context: CallbackContext) -> None:
    try:
        sueldo = float(update.message.text)
        user_id = update.message.from_user.id
        users_data[user_id] = {'sueldo': sueldo, 'saldo': sueldo}
        await update.message.reply_text(f'Tu sueldo quincenal es {sueldo}.', reply_markup=start_keyboard())
    except ValueError:
        await update.message.reply_text('Por favor, ingresa un número válido.', reply_markup=start_keyboard())

    return ConversationHandler.END

# Manejar la entrada de gasto
async def gasto(update: Update, context: CallbackContext) -> None:
    try:
        gasto = float(update.message.text)
        user_id = update.message.from_user.id
        if user_id in users_data:
            users_data[user_id]['saldo'] -= gasto
            saldo_actual = users_data[user_id]['saldo']
            await update.message.reply_text(f'Has gastado {gasto}. Tu saldo actual es {saldo_actual}.', reply_markup=start_keyboard())
        else:
            await update.message.reply_text('Primero ingresa tu sueldo quincenal usando /set_sueldo.', reply_markup=start_keyboard())
    except ValueError:
        await update.message.reply_text('Por favor, ingresa un número válido.', reply_markup=start_keyboard())

    return ConversationHandler.END

# Manejar la entrada de reinicio de sueldo quincenal
async def reiniciar(update: Update, context: CallbackContext) -> None:
    try:
        sueldo = float(update.message.text)
        user_id = update.message.from_user.id
        if user_id in users_data:
            users_data[user_id]['sueldo'] = sueldo
            users_data[user_id]['saldo'] = sueldo
            await update.message.reply_text(f'Tu nuevo sueldo quincenal es {sueldo}. Tu saldo ha sido reiniciado.', reply_markup=start_keyboard())
        else:
            await update.message.reply_text('Primero ingresa tu sueldo quincenal usando /set_sueldo.', reply_markup=start_keyboard())
    except ValueError:
        await update.message.reply_text('Por favor, ingresa un número válido.', reply_markup=start_keyboard())

    return ConversationHandler.END

# Comando /saldo para consultar el saldo actual
async def saldo(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in users_data:
        saldo_actual = users_data[user_id]['saldo']
        await update.message.reply_text(f'Tu saldo actual es {saldo_actual}.')
    else:
        await update.message.reply_text('Primero ingresa tu sueldo quincenal usando /set_sueldo.')

# Comando /help para mostrar los comandos disponibles
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Comandos disponibles:\n"
        "/start - Iniciar el bot y mostrar las opciones\n"
        "/set_sueldo - Establecer el sueldo quincenal\n"
        "/gasto - Registrar un gasto\n"
        "/saldo - Consultar el saldo actual\n"
        "/reiniciar - Reiniciar el sueldo quincenal y el saldo\n"
        "/help - Mostrar esta ayuda"
    )
    await update.message.reply_text(help_text)

# Función para generar el teclado de inicio
def start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Sueldo", callback_data='set_sueldo'),
            InlineKeyboardButton("Gasto", callback_data='gasto'),
            InlineKeyboardButton("Tu Saldo", callback_data='saldo'),
            InlineKeyboardButton("Reiniciar", callback_data='reiniciar'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Función principal para iniciar el bot
def main() -> None:
    # Conectar con el bot de Telegram usando el token
    application = Application.builder().token("7442398402:AAFaqOgvdMCOaYzOvU4ElnZMCqkb56yZDfg").build()

    # Crear el manejador de conversación
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            SET_SUELDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_sueldo)],
            GASTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, gasto)],
            REINICIAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, reiniciar)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Registrar los comandos y manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("saldo", saldo))
    application.add_handler(CommandHandler("help", help_command))

    # Iniciar el bot
    application.run_polling()

if __name__ == '__main__':
    main()
