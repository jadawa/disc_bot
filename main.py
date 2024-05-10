import asyncio
import discord
import requests


# Discord bot token
TOKEN = ""

# OpenAI ChatGPT API endpoint
API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# OpenAI DALL-E API endpoint
DALLE_API_ENDPOINT = "https://api.openai.com/v1/images/generations"

# basic conditions URL
CURRENT_CONDITIONS_URL = "https://weather.api.dtn.com/v2/conditions?lat=44.9484&lon=-93.2991"

# geocoder url
GEOCODER_URL = "https://map.api.dtn.com/v1/geocoder?searchText="

# OpenAI TTS API endpoint
TTS_API_ENDPOINT = "https://api.openai.com/v1/audio/speech"

# OpenAI API key
API_KEY = ""

intents = discord.Intents.default()
intents.message_content = True
# Discord client instance
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Check if the message mentions the bot or starts with a command prefix
    if client.user in message.mentions or message.content.startswith("!bot"):
        # Extract the command or user message without the bot mention or command prefix
        if client.user in message.mentions:
            content = message.content.replace(f"<@!{client.user.id}>", "").strip()
        else:
            content = message.content.replace("!bot", "").strip()

        # Check if the content is a command for chat prompt
        if content.lower() == "chat":
            # Send a prompt message to the user
            prompt_message = await message.channel.send("Please provide a chat prompt:")

            # Wait for the user's response with the chat prompt
            def check_prompt(m):
                return m.author == message.author and m.channel == message.channel

            try:
                prompt_response = await client.wait_for('message', check=check_prompt, timeout=60)
                prompt = prompt_response.content.strip()

                # Send the chat prompt to ChatGPT API for processing
                response = send_to_chatgpt(prompt)

                # Send the response from ChatGPT API to the Discord channel
                await message.channel.send(response)
            except asyncio.TimeoutError:
                await message.channel.send("Prompt response timed out.")

        # Check if the content is a command for image generation
        elif content.lower() == "image":
            # Send a prompt message to the user
            prompt_message = await message.channel.send("Please provide a prompt for the image generation:")

            # Wait for the user's response with the image generation prompt
            def check_prompt(m):
                return m.author == message.author and m.channel == message.channel

            try:
                prompt_response = await client.wait_for('message', check=check_prompt, timeout=60)
                prompt = prompt_response.content.strip()

                # Generate the image using DALL-E API
                image_url = generate_dalle_image(prompt)

                # Send the image URL as a response
                await message.channel.send(image_url)
            except asyncio.TimeoutError:
                await message.channel.send("Prompt response timed out.")

        elif content.lower() == "geocode":
            # Send a prompt message to the user
            prompt_message = await message.channel.send("Please provide an address or city:")

            # Wait for the user's response with the image generation prompt
            def check_prompt(m):
                return m.author == message.author and m.channel == message.channel

            try:
                prompt_response = await client.wait_for('message', check=check_prompt, timeout=60)
                prompt = prompt_response.content.strip()

                # Generate the image using DALL-E API
                image_url = get_geocode(prompt)

                # Send the image URL as a response
                await message.channel.send(image_url)
            except asyncio.TimeoutError:
                await message.channel.send("Prompt response timed out.")

        elif content.lower() == "weather":
            # Send a prompt message to the user
            prompt_message = await message.channel.send("One second please!")

            # Wait for the user's response with the chat prompt
            def check_prompt(m):
                return m.author == message.author and m.channel == message.channel

            try:
                # send request
                response = get_current_conditions()

                # Send the response from ChatGPT API to the Discord channel
                await message.channel.send(response)
            except asyncio.TimeoutError:
                await message.channel.send("Prompt response timed out.")



        elif content.lower() == "commands":
            # Send a prompt message to the user
            prompt_message = await message.channel.send("You can use 'chat', 'image', 'geocode', or 'weather' for now.")
        else:
            # Send the content to ChatGPT API for processing
            response = send_to_chatgpt(content)

            # Send the response from ChatGPT API to the Discord channel
            await message.channel.send(response)


def send_to_chatgpt(message):
    # Prepare headers and payload for ChatGPT API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are ChatGPT Bot"},
            {"role": "user", "content": message}
        ],
        "model": "gpt-3.5-turbo"  # Specify the model to be used
    }

    # Send request to ChatGPT API
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)

    # Check if the API request was successful
    if response.status_code == 200:
        data = response.json()
        # Check if the response contains the expected structure
        if 'choices' in data and data['choices']:
            generated_message = data['choices'][0]['message']['content']
            return generated_message
        else:
            return "Unexpected response from ChatGPT API"
    else:
        return f"ChatGPT API request failed with status code {response.status_code}: {response.text}"


def generate_dalle_image(prompt):
    # Prepare headers and payload for DALL-E API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "quality": "hd",
        "style": "natural",
        "size": "1024x1792"
    }

    # Send request to DALL-E API
    response = requests.post(DALLE_API_ENDPOINT, headers=headers, json=payload)

    # Check if the API request was successful
    if response.status_code == 200:
        data = response.json()
        # Retrieve the generated image URL
        image_url = data['data'][0]['url']
        print(image_url)
        return image_url
    else:
        return f"DALL-E API request failed with status code {response.status_code}: {response.text}"


def get_current_conditions():
    headers = {
        'Authorization': 'Bearer '
    }
    payload = {
    }
    response = requests.request("GET", CURRENT_CONDITIONS_URL, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return data['features'][0]['properties']

    else:
        return f"API request failed with status code {response.status_code}: {response.text}"

def get_geocode(prompt):
    headers = {
        'Authorization': 'Bearer tokenHere'
    }
    payload = {
    }
    updated_url = GEOCODER_URL + prompt

    response = requests.request("GET", updated_url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        return data['features'][0]['center']

    else:
        return f"API request failed with status code {response.status_code}: {response.text}"


# Run the Discord bot
client.run(TOKEN)
