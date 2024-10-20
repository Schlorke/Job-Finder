import discord
import asyncio
from discord import app_commands
from discord.ext import commands
from utils.busca_vagas import buscar_vagas
from utils.interacoes import enviar_vagas_embed, handle_interaction  

# Cor da embed personalizada
embed_color = 0xc1e53f

@discord.app_commands.command(name="vagas", description="Busca vagas de emprego.")
async def vagas_command(ctx: discord.Interaction):  
    embed_instrucoes = discord.Embed(
        title="Oportunidades de Carreira",
        description="Por favor, insira o cargo e a localidade desejados separados por vírgulas.",
        color=embed_color
    )

    embed_instrucoes.add_field(name="Exemplo:", value="Desenvolvedor, São Paulo", inline=False)
    embed_instrucoes.set_footer(
        text="© Desenvolvido por Harry Schlorke com todos os direitos reservados.",
        icon_url="https://images-ext-1.discordapp.net/external/psPtO3F6-Gp2GwZdVOKGA9_fdo-hlU8SxdDU35zOG0g/%3Fsize%3D2048/https/cdn.discordapp.com/avatars/329062794215424003/5201795b96c6a729a7ac961f01739d43.png?format=webp&quality=lossless&width=468&height=468"
    )
    embed_instrucoes.set_image(url="https://i.pinimg.com/originals/1f/f3/3e/1ff33ede4825194fdbcf0f9b5e27dc93.gif")
    embed_instrucoes.set_thumbnail(url="https://media.tenor.com/mN11mgaH9yYAAAAj/hug.gif")

    await ctx.response.send_message(embed=embed_instrucoes)

    def check(msg):
        return msg.author == ctx.user and msg.channel == ctx.channel

    try:
        # Espera o usuário inserir cargo e localidade
        msg = await ctx.client.wait_for('message', check=check, timeout=60)  # Use ctx.client
        cargo, localidade = map(str.strip, msg.content.split(','))

        # Verifica se cargo e localidade foram fornecidos corretamente
        if not cargo or not localidade:
            raise ValueError("Cargo ou localidade não podem estar vazios.")

        # Buscando vagas
        vagas, error = buscar_vagas(cargo, localidade)

        # Inicializa variáveis de controle para paginação
        total_vagas = len(vagas) if vagas else 0
        vagas_por_pagina = 5
        total_paginas = (total_vagas + vagas_por_pagina - 1) // vagas_por_pagina

        # Inicializando a mensagem de carregamento
        initial_message = await ctx.followup.send(embed=discord.Embed(title="Carregando...", description="Por favor, aguarde.", color=embed_color))

        # Lógica para tratar erro 429 (muitas requisições)
        if error and "Erro 429" in error:
            embed_erro_429 = discord.Embed(
                title="Erro 429",
                description="Muitas solicitações. \nTentando novamente após 10 segundos...",
                color=discord.Color.red()
            )
            embed_erro_429.set_thumbnail(url="https://i.sstatic.net/kOnzy.gif")
            await initial_message.edit(embed=embed_erro_429)

            await asyncio.sleep(10)
            vagas, error = buscar_vagas(cargo, localidade)

            if error:
                embed_erro_429.description = "Ainda recebendo erro 429. \nPor favor, tente novamente mais tarde."
                embed_erro_429.set_thumbnail(url="https://cdn3.iconfinder.com/data/icons/computer-emoticon-filled/24/computer_emoticon_emoji-23-512.png")
                await initial_message.edit(embed=embed_erro_429)
                return

        # Se houver outro erro que não seja 429
        if error:
            embed_erro = discord.Embed(
                title="Erro na busca",
                description=f"Ocorreu um erro ao buscar vagas para {cargo} em {localidade}. Tente novamente mais tarde.",
                color=discord.Color.red()
            )
            await initial_message.edit(embed=embed_erro)
            return

        # Envia as vagas encontradas utilizando a função de embed para vagas
        await enviar_vagas_embed(initial_message, vagas, 0, cargo, localidade, total_paginas, total_vagas, vagas_por_pagina)

        # Função para lidar com interações de paginação
        await handle_interaction(ctx, initial_message, vagas, cargo, localidade, total_paginas, total_vagas, vagas_por_pagina)

    except asyncio.TimeoutError:
        # Trata o caso de o usuário não responder no tempo limite
        embed_timeout = discord.Embed(
            title="Tempo Esgotado",
            description="Você não respondeu a tempo. Por favor, tente novamente.",
            color=embed_color
        )
        await ctx.followup.send(embed=embed_timeout)

    except ValueError as ve:
        # Trata o caso de cargo ou localidade não serem fornecidos corretamente
        embed_erro = discord.Embed(
            title="Erro na entrada",
            description=str(ve),
            color=discord.Color.red()
        )
        await ctx.followup.send(embed=embed_erro)
