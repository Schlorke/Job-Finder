import discord
import asyncio
from utils.busca_vagas import buscar_vagas

# Cor da embed personalizada
embed_color = 0xc1e53f

# Função para criar a embed com as vagas da página atual
async def enviar_vagas_embed(message, vagas, pagina, cargo, localidade, total_paginas, total_vagas, vagas_por_pagina):
    if not vagas or total_vagas == 0:
        embed_resultado = discord.Embed(
            title="Oportunidades de Carreira",
            description=f"Nenhuma vaga encontrada para **{cargo}** em **{localidade}**.",
            color=discord.Color.red()
        )
        embed_resultado.set_thumbnail(url="https://cdn3.iconfinder.com/data/icons/computer-emoticon-filled/24/computer_emoticon_emoji-23-512.png")
        await message.edit(embed=embed_resultado, view=None)
        return None, "Nenhuma vaga encontrada para os critérios fornecidos."

    start = pagina * vagas_por_pagina
    end = start + vagas_por_pagina
    vagas_limitadas = vagas[start:end]

    embed_resultado = discord.Embed(
        title="Oportunidades de Carreira",
        description=f"Resultados para **{cargo}** em **{localidade}**:",
        color=embed_color
    )

    for vaga in vagas_limitadas:
        embed_resultado.add_field(name=vaga['company'], value=f"[{vaga['title']}]({vaga['link']})", inline=False)

    # Verifica se há mais vagas e adiciona os botões
    view = discord.ui.View()
    if total_vagas > vagas_por_pagina:
        if pagina > 0:
            view.add_item(discord.ui.Button(label="Anterior", style=discord.ButtonStyle.secondary, custom_id="previous"))
        if pagina < total_paginas - 1:
            view.add_item(discord.ui.Button(label="Próximo", style=discord.ButtonStyle.secondary, custom_id="next"))

    # Mantém a imagem e a thumbnail
    embed_resultado.set_image(url="https://i.pinimg.com/originals/1f/f3/3e/1ff33ede4825194fdbcf0f9b5e27dc93.gif")
    embed_resultado.set_thumbnail(url="https://media.tenor.com/mN11mgaH9yYAAAAj/hug.gif")

    await message.edit(embed=embed_resultado, view=view)

    return vagas, None

# Função para lidar com a interação com os botões e resetar o timeout
async def handle_interaction(ctx, message, vagas, cargo, localidade, total_paginas, total_vagas, vagas_por_pagina):
    pagina_atual = 0

    async def remove_buttons():
        await asyncio.sleep(60)  # Espera 60 segundos
        try:
            await message.edit(view=None)  # Remove os botões mantendo a embed
        except discord.NotFound:
            pass  # Mensagem ou interação não encontrada

    remove_task = asyncio.create_task(remove_buttons())

    while True:
        try:
            interaction = await ctx.client.wait_for("interaction", check=lambda inter: inter.user == ctx.user and inter.message.id == message.id, timeout=60)

            # Cancela a remoção de botões ao detectar interação e reinicia o timeout
            remove_task.cancel()
            remove_task = asyncio.create_task(remove_buttons())

            custom_id = interaction.data['custom_id']

            if custom_id == "next":
                pagina_atual += 1
            elif custom_id == "previous":
                pagina_atual -= 1

            # Atualiza as vagas na embed
            await enviar_vagas_embed(interaction.message, vagas, pagina_atual, cargo, localidade, total_paginas, total_vagas, vagas_por_pagina)

            # Responde à interação sem tentar enviar uma nova mensagem
            await interaction.response.defer()

        except asyncio.TimeoutError:
            break
        except discord.NotFound:
            break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            break
