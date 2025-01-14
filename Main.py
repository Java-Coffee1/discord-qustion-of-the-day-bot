import discord
import json
from discord.ext import tasks, commands
import asyncio
from datetime import datetime
import pytz
import random



# Load the bot token and initialize intents
with open("oldconfig.json") as config_file:
    config = json.load(config_file)
intents = discord.Intents.default()
intents.message_content = True
TOKEN = config["TOKEN"]
qotd_role_name = config["qotd_role_name"]
qotd_channel_id = config["qotd_channel_id"]
ADMIN_USER_ID = 770668417367670866
role_to_add_questions = config["role_to_add_questions"]
send_message = config["send_message"]  # Time to send QOTD (in 24-hour format)
Timezone = config["Timezone"]
aotd_channel_id = config["aotd_channel_id"]
low_question_channel = config["low_question_channel"]
notify_channel_id = config["notify_channel_id"]
# ----------------- Functions -----------------
# File to store questions
QUESTIONS_FILE = "questions.json"
OPEN_COMMANDS = ["!help", "!credits"] #any one can use these commands

# Ensure the questions file exists
def initialize_questions_file():
    try:
        with open(QUESTIONS_FILE, "r") as f:
            json.load(f)  # Validate JSON format
    except (FileNotFoundError, json.JSONDecodeError):
        with open(QUESTIONS_FILE, "w") as f:
            json.dump({"questions": []}, f)  # Initialize an empty list for questions

initialize_questions_file()

# Helper functions for JSON operations
def save_question_to_json(question, user):
    nickname = user.nick if user.nick else user.name
    user_id = user.id # Get nickname or fallback to username
    with open(QUESTIONS_FILE, "r+") as f:
        data = json.load(f)
        #data["questions"].append(question)
        data["questions"].append({"question": question, "user": nickname, "user_id": user_id})
        f.seek(0)
        json.dump(data, f, indent=4)

def get_all_questions_from_json():
    with open(QUESTIONS_FILE, "r") as f:
        data = json.load(f)
    return data["questions"]
    if not questions:
        return "The question queue is currently empty."
    return "\n".join(f"{idx + 1}. {q}" for idx, q in enumerate(questions))

def get_latest_question_from_json():
    questions = get_all_questions_from_json()
    return questions[0] if questions else None  # Fetch the first question (FIFO)

def remove_latest_question_from_json():
    """Remove the most recent question from the JSON file."""
    with open(QUESTIONS_FILE, "r+") as f:
        data = json.load(f)
        if data["questions"]:  # Ensure there are questions to remove
            data["questions"].pop(0)  # Remove the first question (FIFO order)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

def low_questions(threshold=5):
    """Check if the number of saved questions is below a certain threshold."""
    questions = get_all_questions_from_json()
    return len(questions) < threshold

async def notify_low_questions():
    """Send a notification if questions are running low."""
    if low_questions():  # Assuming this function returns True when the queue is low
        if notify_channel_id:  # Ensure the channel ID is defined
            channel = client.get_channel(int(notify_channel_id))
            if channel:
                await channel.send("⚠️ The question queue is running low! Please add more questions.")
        else:  # Fall back to notifying the admin directly
            admin_user = await client.fetch_user(ADMIN_USER_ID)
            if admin_user:
                await admin_user.send("⚠️ The question queue is running low! Please add more questions.")




async def post_qotd(channel):
    guild = channel.guild
    channel = client.get_channel(int(str(qotd_channel_id)) )
    role = discord.utils.get(guild.roles, name=qotd_role_name)  # Fetch the QOTD role
    latest_question = get_latest_question_from_json()
    if latest_question:
        aotd_channel = await client.fetch_channel(aotd_channel_id)
        channel_mention=f"<#{aotd_channel.id}>"
        question = latest_question["question"]
        user_id = latest_question["user_id"]  # Get the saved user ID
        if role:
            await channel.send(f"{role.mention}\n\n{question}\n\nQuestion submitted by: <@{user_id}>\nShare your thoughts in {channel_mention}")
            #await channel.send(f"{role.mention}\n\n{latest_question}n\n share your thoughts in the {channel_mention}")
            remove_latest_question_from_json()
        else:
            await channel.send(f"The role `{qotd_role_name}` does not exist in this server.")
    else:
        await channel.send("No questions saved yet.")


# ----------------- End Functions -----------------

# ----------------- Client and Timer -----------------

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        # Start the QOTD task loop after the bot is ready
        self.send_qotd_task.start()

    async def on_message(self, message):
        # Ignore the bot's own messages
        if message.author.bot:
            return
        if message.guild is None:
            await message.channel.send("This command can only be used in a server.")
            return
        if not message.content.startswith("!"):
            return
        # Extract the command (e.g., "!help")
        command = message.content.split()[0].lower()
        if command in OPEN_COMMANDS:
        # Process open commands
            if command == "!help":
                help_message = (
                    "**📖 Bot Help Guide**\n\n"
                   "**General Commands:**\n"
                    "• `!credits` - View credits for the bot's creation.\n"
                    "• `!help` - Display this help message.\n\n"
                    "**QOTD Commands:**\n"
                    "• `!saveqotd ```your question here``` ` - Save a new Question of the Day (QOTD).\n"
                    "  - Example: `!saveqotd ```What's your favorite hobby?``` `\n"
                    "• `!qotd_queue` - Will DM you all of the questions in the queue.\n"
                    "• `!manualqotd` - Manually post a QOTD to the current channel.\n\n"
                    "• `!shutdown` - Will SHUT DOWN THE BOT.\n"
                    f"If you have further questions, please contact <@{ADMIN_USER_ID}>."
                )   
                await message.channel.send(help_message)

            elif command == "!credits":
                await message.channel.send(
                    "Bot made by <@770668417367670866>\n"
                    "Profile pic by Ryoshi\n"
                    "Bot creation date: December 6, 2024"
                    'Bot fucked up date Jan/13/2025'
                )
            return


        
        if await self.user_check(message):
            return
        # Save a question command also only admins can use this commands
        if command == "!saveqotd":
            if "```" in message.content:
                try:
                    question = message.content.split("```")[1].strip()  # Extract and clean the content inside triple backticks
                    #save_question_to_json(question)
                    save_question_to_json(question, message.author)
                    sent_message = await message.channel.send("Your question has been saved.")
                    await asyncio.sleep(3)
                    await message.delete()
                    await sent_message.delete()
                except IndexError:
                    sent_message = await message.channel.send("To save a question do this (!saveqotd \`\`\` your question here \`\`\`)")
                    await asyncio.sleep(4)  
                    await message.delete()
                    await sent_message.delete()
            else:
                sent_message = await message.channel.send("To save a question do this (!saveqotd \`\`\` your question here \`\`\`)")
                await asyncio.sleep(4)  
                await message.delete()
                await sent_message.delete()
        elif command == "!manualqotd":
            await post_qotd(message.channel)

        elif command == "!qotd_queue":
            questions = get_all_questions_from_json()
            if not questions:
                await message.author.send("The question queue is currently empty.")
            else:
                formatted_questions = "\n".join(
                f"{idx + 1}. {q['question']} (Submitted by: {q['user']})"
                for idx, q in enumerate(questions)
                )
                try:
                    await message.author.send(f"📋 **Question Queue:**\n{formatted_questions}")
                    print(f"Sent QOTD queue to {message.author}")
                except discord.Forbidden:
                    await message.channel.send(
                    "I couldn't DM you the question queue. Please ensure your DMs are enabled."
                    )
        elif command == "!shutdown":
            # Notify admin about the shutdown
            admin_user = await self.fetch_user(ADMIN_USER_ID)  # Replace with your admin user ID
            user_mention = f"<@{message.author.id}>"  # Mention the user
            shutdown_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            shutdown_message = (
                f"🛑 **Shutdown Alert**\n\n"
                f"**User:** {user_mention}\n"
                f"**Time:** {shutdown_time}\n\n"
                f"The bot was shut down by this user."
            )
            if admin_user:
                try:
                    await admin_user.send(shutdown_message)
                    print(f"Shutdown log sent to admin: {admin_user}")
                except discord.Forbidden:
                    print("Failed to send shutdown log to admin. Ensure the admin's DMs are open.")

            # Notify the channel and shut down
            await message.channel.send(f"Shutting down... Goodbye!")
            await self.close()  # Shut down the bot

# User Check Funtions
    async def user_check(self, message):
        if not self.is_authorized(message.author, message.guild):
            sent_message = await message.channel.send(
            f"{message.author.mention}, you are not authorized to perform this action. Please contact an admin.")
            await asyncio.sleep(5)
            await sent_message.delete()
            await message.delete()
            return True
        return False

    def is_authorized(self, user, guild):
        """Check if the user is either an admin or has the Mods role."""
        # Check if the user is the admin
        if user.id == ADMIN_USER_ID:
            return True

        # Ensure we have a valid guild and user is a member of it
        if not guild or not isinstance(user, discord.Member):
            return False

        # Check if the user has the "Mods" role
        role = discord.utils.get(user.roles, name=role_to_add_questions)
        return role is not None


    @tasks.loop(minutes=1)
    async def send_qotd_task(self):
        # Check if it's the scheduled time for the QOTD
        tz = pytz.timezone(Timezone)
        now = datetime.now(tz)
        scheduled_time = datetime.strptime(send_message, "%H:%M").time()
        if now.time().hour == scheduled_time.hour and now.time().minute == scheduled_time.minute:
            channel = self.get_channel(int(str(qotd_channel_id)))
            if channel:
                await post_qotd(channel)
                print("QOTD sent!")
            await notify_low_questions()



# Run the bot
client = Client(intents=intents)
client.run(TOKEN)
