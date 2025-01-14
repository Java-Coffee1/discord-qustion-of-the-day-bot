# Discord QOTD Bot

This Discord bot automates the posting of a Question of the Day (QOTD) in a specified channel and allows users with appropriate roles to add questions to the queue. It also supports Docker deployment for easy setup and management.

---

## Features
- Post a daily Question of the Day (QOTD) at a specified time.
- Save and manage a queue of questions.
- Role-based authorization for adding questions.
- Manual and automatic QOTD posting.

---

## Commands
### **1. Save a Question**
**Command:** `!saveqotd`

**Format:**


**Description:** Saves a new question to the queue. Use triple backticks (` ``` `) around the question text.

---

### **2. Manually Post QOTD**
**Command:** `!manualqotd`

**Description:** Posts the next question from the queue to the QOTD channel immediately.

---

## Setup

### **1. Prerequisites**
- Python 3.8+
- Docker (for containerized deployment)
- A Discord bot token

---

### **2. Configuration**
Create a `config.json` file in the root directory of the project:

```json
{
  "TOKEN": "YOUR_DISCORD_BOT_TOKEN",
  "qotd_role_name": "QOTD",
  "qotd_channel_id": 123456789012345678,
  "ADMIN_USER_ID": 123456789,
  "role_to_add_questions": "Mods",
  "send_message": "15:00",
  "Timezone": "Your Time Zone"
}

```
TOKEN: Your Discord bot token.
qotd_role_name: The name of the role to mention in QOTD posts.
qotd_channel_id: The ID of the channel where QOTD should be posted.
ADMIN_USER_ID: Your Discord user ID for admin rights.
role_to_add_questions: Role name allowed to add questions.
send_message: Time to send QOTD in 24-hour format (e.g., 15:00).
Timezone: Timezone for scheduling (e.g., America/Vancouver).




### **3. Depoly with docker**


``` Dockerfile
# Use Python 3.10 image as base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy necessary files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]

```

### **3. Build**

docker build -t discord-qotd-bot .
**Command:** `docker build -t discord-qotd-bot .`

### **4. Run**
**Command:** `docker compose up -d`

### **5. example compose file**

``` docker-compose.yml

version: "3.8"

services:
  discord-bot:
    build: .
    container_name: bot-furlumbians
    volumes:
      - /path to bot:/app
      - /path/to/config/config.json:/app/config.json
    restart: always

```




