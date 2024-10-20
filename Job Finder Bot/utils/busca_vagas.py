import requests
from bs4 import BeautifulSoup

# Função para buscar vagas de emprego no LinkedIn
def buscar_vagas(cargo, localidade):
    url = f'https://www.linkedin.com/jobs/search/?keywords={cargo}&location={localidade}'
    response = requests.get(url)

    # Verificando se houve erro 429
    if response.status_code == 429:
        return None, "Erro 429: Muitas solicitações. Tente novamente mais tarde."

    if response.status_code != 200:
        return None, f"Erro ao acessar a página: {response.status_code} para URL {url}"

    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrando os elementos que contêm as informações das vagas
    vagas = []
    for job_card in soup.find_all('div', class_='job-search-card'):
        title = job_card.find('h3')
        company = job_card.find('h4')
        link = job_card.find('a', href=True)

        if title and company and link:
            vagas.append({
                'title': title.get_text(strip=True),
                'company': company.get_text(strip=True),
                'link': link['href']
            })

    return vagas, None  # Retornando a lista de vagas e None para erro
