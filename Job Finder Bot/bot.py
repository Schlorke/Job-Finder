import discord
from discord.ext import commands
from config import TOKEN
from commands.vagas import vagas_command  # Importa o comando 'vagas'

# Configura os intents do bot
intents = discord.Intents.default()
intents.message_content = True

# Inicializa o bot
bot = commands.Bot(command_prefix="/", intents=intents)

# Evento para indicar quando o bot está pronto
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.tree.add_command(vagas_command)  # Adiciona o comando 'vagas' à árvore de comandos

# Executa o bot
bot.run(TOKEN)  # Insira seu token aqui
