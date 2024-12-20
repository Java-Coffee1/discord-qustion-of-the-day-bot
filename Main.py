import discord
import json
from discord.ext import tasks
import asyncio
from datetime import datetime
import pytz
import random

# Load the bot token and initialize intents
with open("config.json") as config_file:
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

# ----------------- Functions -----------------
# File to store questions
QUESTIONS_FILE = "questions.json"

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
    admin_user = await client.fetch_user(ADMIN_USER_ID)
    guild = discord.utils.get(client.guilds)  # Use the first guild (server) the bot is connected to
    notify_channel = discord.utils.get(guild.text_channels, name="suggestions")  # Specify a notification channel

    if low_questions():
        if notify_channel:
            await notify_channel.send("⚠️ The question queue is running low! Please add more questions.")
        elif admin_user:
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
        if message.author == self.user:
            return
        
        if message.content.lower().startswith("uwu"):
            if random.randint(1, 10) == 1:
                await message.channel.send("owo")
        elif message.content.lower().startswith("owo"):
            if random.randint(1, 20) == 1:
                await message.channel.send("uwu")
        elif message.content.lower().startswith("meow"):
            if random.randint(1, 40) == 1:
                await message.channel.send("meowmeow")
        elif message.content.lower().startswith("∩^ω^∩"):
                if random.randint(1, 30) == 1:
                    await message.channel.send("(｡♥‿♥｡)")
        elif message.content.lower().startswith("skibidi"):
            if random.randint(1, 3) == 1:
                await message.channel.send("sigma sigma on the wall whoes the skibidis of them all")
        elif message.content.lower().startswith("crazy"):
            if random.randint(1, 35) == 1:
                await message.channel.send("crazy? I was crazy once they lock me in a room a ruber room a ruber room with rats\n"
                "crazy,I was crazy once they lock me in a room a ruber room a ruber room with ratsn\n"
                "crazy,I was crazy once they lock me in a room a ruber room a ruber room with ratsn\n"
                "crazy,I was crazy once they lock me in a room a ruber room a ruber room with ratsn\n"
                "crazy,I was crazy once they lock me in a room a ruber room a ruber room with ratsn\n"
                "crazy,I was crazy once they lock me in a room a ruber room a ruber room with ratsn\n"
                "crazy,I was crazy once they lock me in a room a ruber room a ruber room with ratsn\n"
                "crazy,I was crazy once they lock me in a room a ruber room a ruber room with ratsn\n"
                "crazy,I was crazy once they lock me in a room a ruber room a ruber room with ratsn\n"
                )
        elif message.content.lower().startswith("woof"):
            if random.randint(1, 5) == 1:
                await message.channel.send("woof woof")
        elif message.content.lower().startswith("arf"):
            if random.randint(1, 5) == 1:
                await message.channel.send("arf arf")
        elif message.content.lower().startswith("bark"):
            if random.randint(1, 5) == 1:
                await message.channel.send("woof")
        if message.content.lower().startswith("!credits"):
            await message.channel.send(
                "Bot made by <@770668417367670866>\n"
                "Profile pic by Ryoshi\n"
                "Bot creation date: December 6, 2024"
            )

        # user check
        if not self.is_authorized(message.author):
            return
        # Save a question command
        if message.content.startswith("!saveqotd"):
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
        elif message.content.startswith("!manualqotd"):
            await post_qotd(message.channel)


    def is_authorized(self, user):
        """Check if the user is either an admin or has the Mods role."""
        # Check if the user is the admin
        if user.id == ADMIN_USER_ID:
            return True

        # Check if the user has the "Mods" role
        role = discord.utils.get(user.roles, name=role_to_add_questions)
        if role:
            return True

        return False

    @tasks.loop(minutes=1)
    async def send_qotd_task(self):
        # Check if it's the scheduled time for the QOTD
        tz = pytz.timezone(Timezone)
        now = datetime.now(tz)
        scheduled_time = datetime.strptime(send_message, "%H:%M").time()
        print("Scheduled time:", scheduled_time)

        if now.time().hour == scheduled_time.hour and now.time().minute == scheduled_time.minute:
            channel = self.get_channel(int(str(qotd_channel_id)))
            print("QOTD time!")
            if channel:
                await post_qotd(channel)
                print("QOTD sent!")
            await notify_low_questions()


# Run the bot
client = Client(intents=intents)
client.run(TOKEN)
