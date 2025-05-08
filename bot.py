import discord
from discord import app_commands
from discord.ext import commands
import os
from datetime import datetime

# Intents and bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# File size limit (in bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# File modification logic
def modify_file_and_save(second_file_data, png_data):
    marker = b'\x89PNG\r\n\x1a\n'
    if marker in second_file_data:
        trimmed_data = second_file_data.split(marker)[0]
        return trimmed_data + png_data
    return None

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'✅ Logged in as {bot.user} and slash commands synced!')

@bot.tree.command(name="replaceimage", description="Replace everything after '‰PNG' in file 2 with data from PNG file 1.")
@app_commands.describe(png_file="The PNG image file", target_file="The file to be modified")
async def replaceimage(interaction: discord.Interaction, png_file: discord.Attachment, target_file: discord.Attachment):
    await interaction.response.defer()
    
    try:
        user = interaction.user
        print(f"[{datetime.now()}] 🔧 User '{user}' triggered /replaceimage")

        # File size check
        if png_file.size > MAX_FILE_SIZE or target_file.size > MAX_FILE_SIZE:
            await interaction.followup.send("❌ One or both files exceed the 5MB size limit. Please upload smaller files.")
            print(f"[{datetime.now()}] 🚫 File size too large. PNG: {png_file.size} bytes, TARGET: {target_file.size} bytes")
            return

        # Read files
        png_data = await png_file.read()
        target_data = await target_file.read()

        print(f"[{datetime.now()}] 📄 Files received: PNG='{png_file.filename}' ({len(png_data)} bytes), TARGET='{target_file.filename}' ({len(target_data)} bytes)")

        # Process and replace
        result = modify_file_and_save(target_data, png_data)

        if result:
            base_name, ext = os.path.splitext(target_file.filename)
            new_filename = f"edit-{base_name}{ext}"

            with open(new_filename, 'wb') as f:
                f.write(result)

            print(f"[{datetime.now()}] ✅ File processed and saved as '{new_filename}'")

            await interaction.followup.send(
                content=f"✅ Done! Here's your modified file:",
                file=discord.File(new_filename)
            )

            os.remove(new_filename)
            print(f"[{datetime.now()}] 🧹 Temporary file deleted: {new_filename}")
        else:
            await interaction.followup.send("⚠️ Could not find PNG marker in the second file.")
            print(f"[{datetime.now()}] ⚠️ PNG marker not found in '{target_file.filename}'")

    except Exception as e:
        await interaction.followup.send(f"❌ Error occurred: {str(e)}")
        print(f"[{datetime.now()}] ❌ Error: {e}")

# --- YOUR TOKEN HERE ---
bot.run("YOUR_BOT_TOKEN_HERE")
