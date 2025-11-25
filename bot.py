from dotenv import load_dotenv
import discord
import json
import os
from discord.ext import commands

load_dotenv()

def load_boss_data():
    if not os.path.exists('tarkov_boss_spawns.json'):
        return None
    with open('tarkov_boss_spawns.json', 'r', encoding='utf-8') as f:
        return json.load(f)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')

@bot.command(name='bosses')
async def bosses(ctx, *, query: str = None):
    data = load_boss_data()
    if not data:
        await ctx.send("❌ No se encontró el archivo `tarkov_boss_spawns.json`.")
        return

    maps = data['maps']

    if not query:
        summary = "**🗺️ Mapas disponibles:**\n"
        for map_name in maps:
            summary += f"- {map_name}\n"
        summary += "\nEscribe `!bosses NombreDelMapa` o `!bosses NombreDelBoss`"
        await ctx.send(summary)
        return

    query = query.strip()

    # Buscar por mapa
    if query in maps:
        boss_list = maps[query]
        response = f"**📍 Bosses en {query}:**\n"
        for b in boss_list:
            locs = ', '.join(b['locations']) if b['locations'] else "Sin ubicación"
            response += f"\n**{b['boss']}** • {b['spawn_chance']} • {locs}"
        if len(response) > 2000:
            response = response[:1990] + "...\n(truncado por límite de Discord)"
        await ctx.send(response)
        return

    # Buscar por boss
    found = []
    for map_name, bosses in maps.items():
        for boss in bosses:
            if boss['boss'].lower() == query.lower():
                found.append((map_name, boss))

    if found:
        response = f"**🔍 '{query}' aparece en:**\n"
        for map_name, boss in found:
            locs = ', '.join(boss['locations']) if boss['locations'] else "Sin ubicación"
            response += f"\n**{map_name}**: {boss['spawn_chance']} • {locs}"
        if len(response) > 2000:
            response = response[:1990] + "...\n(truncado)"
        await ctx.send(response)
        return

    await ctx.send(f"❌ No se encontró '{query}'. Usa `!bosses` para ver mapas.")

# ⚠️ PON TU TOKEN AQUÍ ⚠️
bot.run(os.getenv("token"))