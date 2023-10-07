import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from uuid import uuid4

# Replace 'YOUR_API_TOKEN' with your actual API Token
TOKEN = '5988803366:AAG8MtLg6nrMGsh6siejtJvzD86fZ9gRKoI'
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Define states for the conversation
CREATE_POST, SEND_POST, MODIFY_POST, CREATE_SINGLE_LINK, CREATE_MULTIPLE_LINK, CONTACT_USER, REPLY_ADMIN, SHOW_FEATURES = range(8)

# Dictionary to store posts
posts = {}
# Dictionary to store file links
file_links = {}
# Dictionary to store user messages
user_messages = {}
# Dictionary to store admin replies
admin_replies = {}

# Replace 'YOUR_ADMIN_TELEGRAM_ID' with the actual admin's Telegram ID
ADMIN_TELEGRAM_ID = '@SamRB09'

# Function to start the conversation
def start(update, context):
    user = update.effective_user
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Welcome to PocketFmEnglish_Bot, {user.first_name}! Click the buttons below to explore.",
        reply_markup=get_main_menu_keyboard(),
    )
    return CREATE_POST

# Function to create a post
def create_post(update, context):
    context.user_data['post_id'] = str(uuid4())
    update.message.reply_text("Please enter your post:")
    return SEND_POST

# Function to send the post
def send_post(update, context):
    post_id = context.user_data['post_id']
    posts[post_id] = update.message.text
    update.message.reply_text("Your post has been created. What would you like to do next?", reply_markup=get_main_menu_keyboard())
    return CREATE_POST

# Function to modify a post
def modify_post(update, context):
    user = update.effective_user
    update.message.reply_text("Here are your posts:")
    for post_id, post_text in posts.items():
        keyboard = [
            [InlineKeyboardButton("Edit", callback_data=f"edit_post:{post_id}")],
            [InlineKeyboardButton("Delete", callback_data=f"delete_post:{post_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"Post ID: {post_id}\n{post_text}", reply_markup=reply_markup)

    update.message.reply_text("Choose a post to edit or delete, or click 'Back' to return to the main menu.")
    return MODIFY_POST

# Callback function to edit or delete a post
def edit_or_delete_post(update, context):
    query = update.callback_query
    query.answer()
    action, post_id = query.data.split(':')

    if action == "edit_post":
        context.user_data['post_id'] = post_id
        query.edit_message_text("Please enter the new text for your post:")
        return SEND_POST
    elif action == "delete_post":
        if post_id in posts:
            del posts[post_id]
            query.edit_message_text("The post has been deleted.")
        else:
            query.edit_message_text("Post not found.")

    update.callback_query.message.reply_text("What would you like to do next?", reply_markup=get_main_menu_keyboard())
    return CREATE_POST

# Function to create a single file link
def create_single_link(update, context):
    link_id = str(uuid4())
    file_links[link_id] = update.message.document.file_id
    update.message.reply_text(f"File link created: {link_id}", reply_markup=get_main_menu_keyboard())

    # Automatically send a message to join the channel
    join_message = "Join for more stories"
    join_button = InlineKeyboardButton("Join Now", url="https://t.me/PocketFmEnglish2")
    join_markup = InlineKeyboardMarkup([[join_button]])
    update.message.reply_text(join_message, reply_markup=join_markup)

    return CREATE_POST

# Function to create multiple file links
def create_multiple_links(update, context):
    link_ids = []
    for _ in range(3):  # You can adjust the number of links to create
        link_id = str(uuid4())
        file_links[link_id] = update.message.document.file_id
        link_ids.append(link_id)
    update.message.reply_text(f"File links created: {', '.join(link_ids)}", reply_markup=get_main_menu_keyboard())

    # Automatically send a message to join the channel
    join_message = "Join for more stories"
    join_button = InlineKeyboardButton("Join Now", url="https://t.me/PocketFmEnglish2")
    join_markup = InlineKeyboardMarkup([[join_button]])
    update.message.reply_text(join_message, reply_markup=join_markup)

    return CREATE_POST

# Function to contact user by sending a message to admin
def contact_user(update, context):
    user = update.effective_user
    user_message = update.message.text

    if ADMIN_TELEGRAM_ID:
        user_messages[user.id] = user_message
        context.bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=f"Message from user {user.username}:\n{user_message}")
        update.message.reply_text("Your message has been sent to the admin.", reply_markup=get_main_menu_keyboard())
    else:
        update.message.reply_text("Sorry, the admin's Telegram ID is not configured.", reply_markup=get_main_menu_keyboard())

    return CREATE_POST

# Function to list the number of users with their usernames
def list_users(update, context):
    users = context.bot.get_chat_members_count(update.effective_chat.id)
    update.message.reply_text(f"Number of users in this chat: {users}", reply_markup=get_main_menu_keyboard())
    return CREATE_POST

# Function to send a message to bot admin
def send_message_to_admin(update, context):
    update.message.reply_text("Please enter your message for the admin:")
    return CONTACT_USER

# Function to reply to a user from the admin side
def reply_to_user(update, context):
    user = update.effective_user
    admin_message = update.message.text
    user_id = context.user_data.get('last_user_id')

    if user_id:
        context.bot.send_message(chat_id=user_id, text=f"Reply from admin:\n{admin_message}")
        update.message.reply_text("Your reply has been sent to the user.", reply_markup=get_main_menu_keyboard())
    else:
        update.message.reply_text("Sorry, there was an issue replying to the user.", reply_markup=get_main_menu_keyboard())

    return CREATE_POST

# Function to show the menu with feature descriptions
def show_features(update, context):
    features_text = """Available Features:
    1. Create a Post
    2. Modify a Post (Create, Edit, Delete)
    3. Create Single File Link
    4. Create Multiple File Links
    5. Send a Message to Admin
    6. List Users
    7. Contact Admin
    8. View Features Menu
    9. Check Webhook Status (/getWebhookInfo)
    """
    update.message.reply_text(features_text, reply_markup=get_main_menu_keyboard())
    return CREATE_POST

# Function to check webhook status
def get_webhook_info(update, context):
    webhook_info = context.bot.get_webhook_info()
    update.message.reply_text(f"Webhook URL: {webhook_info.url}\nIs Webhook Set: {webhook_info.has_custom_certificate}\n"
                              f"Pending Updates: {webhook_info.pending_update_count}", reply_markup=get_main_menu_keyboard())
    return CREATE_POST

# Function to handle unknown commands
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I don't understand that command.")

# Function to get the main menu keyboard
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Create a Post", callback_data="create_post")],
        [InlineKeyboardButton("Modify a Post", callback_data="modify_post")],
        [InlineKeyboardButton("Create Single File Link", callback_data="create_single_link")],
        [InlineKeyboardButton("Create Multiple File Links", callback_data="create_multiple_links")],
        [InlineKeyboardButton("Send a Message to Admin", callback_data="send_message_to_admin")],
        [InlineKeyboardButton("List Users", callback_data="list_users")],
        [InlineKeyboardButton("Contact Admin", callback_data="contact_admin")],
        [InlineKeyboardButton("View Features Menu", callback_data="show_features")],
        [InlineKeyboardButton("Check Webhook Status", callback_data="get_webhook_info")],  # New button
    ]
    return InlineKeyboardMarkup(keyboard)

# Define the conversation handler
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CREATE_POST: [
            CommandHandler('start', start),
            CallbackQueryHandler(create_post, pattern='^create_post$'),
            CallbackQueryHandler(modify_post, pattern='^modify_post$'),
            CallbackQueryHandler(create_single_link, pattern='^create_single_link$'),
            CallbackQueryHandler(create_multiple_links, pattern='^create_multiple_links$'),
            CallbackQueryHandler(send_message_to_admin, pattern='^send_message_to_admin$'),
            CallbackQueryHandler(list_users, pattern='^list_users$'),
            CallbackQueryHandler(contact_user, pattern='^contact_admin$'),
            CallbackQueryHandler(show_features, pattern='^show_features$'),
            CallbackQueryHandler(get_webhook_info, pattern='^get_webhook_info$'),  # New callback
        ],
        SEND_POST: [MessageHandler(Filters.text, send_post)],
        MODIFY_POST: [CallbackQueryHandler(edit_or_delete_post)],
        CONTACT_USER: [MessageHandler(Filters.text, contact_user)],
        REPLY_ADMIN: [MessageHandler(Filters.text, reply_to_user)],
    },
    fallbacks=[],
)

dispatcher.add_handler(conversation_handler)
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Start the bot
updater.start_polling()
updater.idle()
