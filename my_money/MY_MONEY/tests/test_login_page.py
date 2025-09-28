import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service # Para especificar o caminho do ChromeDriver, se necessário
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configurações ---
# Especifique o caminho para o seu ChromeDriver se não estiver no PATH
# Exemplo: CHROME_DRIVER_PATH = '/caminho/para/seu/chromedriver'
# Se estiver no PATH, você pode deixar como None ou remover a linha 'service=service_obj' abaixo.
CHROME_DRIVER_PATH = None # Modifique se necessário

LOGIN_URL = 'http://localhost:5000/login'
TEST_EMAIL = 'teste@exemplo.com'
TEST_PASSWORD = 'senha123' # Use uma senha válida ou inválida dependendo do que quer testar

# --- Inicializar o WebDriver ---
if CHROME_DRIVER_PATH:
    service_obj = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service_obj)
else:
    driver = webdriver.Chrome() # Tenta encontrar o ChromeDriver no PATH

driver.implicitly_wait(5) # Espera implícita para elementos

try:
    print(f"Acessando a página de login: {LOGIN_URL}")
    driver.get(LOGIN_URL)
    time.sleep(1) # Pequena pausa para visualização

    # --- Etapa 1: Preencher o campo de e-mail e clicar em login ---
    print(f"Preenchendo o campo de e-mail com: {TEST_EMAIL}")
    email_field = driver.find_element(By.ID, 'email')
    email_field.send_keys(TEST_EMAIL)
    time.sleep(1)

    print("Clicando no botão 'Entrar' (apenas com e-mail preenchido)...")
    # O botão de login está dentro de um formulário e é do tipo submit
    # No seu HTML: <button type="submit" class="btn btn-success w-100">Entrar</button>
    login_button = driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]')
    login_button.click()
    time.sleep(1)

    # Observação: Após este clique, o comportamento esperado pode variar.
    # Como o campo de senha é 'required' no HTML,
    # o navegador pode impedir a submissão do formulário ou exibir uma mensagem de validação.
    # Um teste real verificaria esse comportamento.
    print("Comportamento após clicar com apenas e-mail preenchido (verifique o navegador).")
    print("O campo senha é obrigatório, então o formulário não deve ter sido submetido com sucesso.")
    time.sleep(2)


    # --- Etapa 2: Preencher o campo de senha (e e-mail novamente, caso tenha sido limpo) e clicar em login ---
    # É uma boa prática re-localizar os elementos se a página recarregou ou mudou.
    # Se o e-mail não foi limpo, não precisa preencher de novo.
    # Para este exemplo, vamos limpar e preencher ambos para garantir.

    print("Recarregando a página de login para um novo teste (ou limpando campos)...")
    driver.get(LOGIN_URL) # Recarrega para garantir um estado limpo, ou você pode limpar os campos.
    time.sleep(1)

    print(f"Preenchendo o campo de e-mail com: {TEST_EMAIL}")
    email_field = driver.find_element(By.ID, 'email') # Localiza o campo de e-mail
    email_field.clear() # Limpa caso haja algo
    email_field.send_keys(TEST_EMAIL)
    time.sleep(1)

    print(f"Preenchendo o campo de senha com: {TEST_PASSWORD}")
    password_field = driver.find_element(By.ID, 'senha') # Localiza o campo de senha
    password_field.clear()
    password_field.send_keys(TEST_PASSWORD)
    time.sleep(1)

    print("Clicando no botão 'Entrar' (com e-mail e senha preenchidos)...")
    login_button = driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]') # Localiza o botão de login
    login_button.click()
    time.sleep(2) # Pausa para ver o resultado (redirecionamento ou mensagem de erro)

    # --- Verificações (Asserções) ---
    # Em um teste real, você adicionaria asserções aqui para verificar o resultado.
    # Por exemplo, se o login for bem-sucedido, verificar se a URL mudou para o dashboard.
    # Se o login falhar, verificar se uma mensagem de erro é exibida.

    current_url = driver.current_url
    if "dashboard" in current_url:
        print("Login aparentemente bem-sucedido! Redirecionado para o dashboard.")
    elif LOGIN_URL in current_url: # Se permaneceu na página de login
        # Tenta encontrar uma mensagem de erro flash (exemplo)
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".text-danger")) # Ajuste o seletor conforme suas mensagens flash
            )
            if error_message and error_message.is_displayed():
                print(f"Login falhou. Mensagem de erro encontrada: '{error_message.text}'")
            else:
                print("Login falhou. Nenhuma mensagem de erro específica encontrada (verifique o HTML).")
        except:
            print("Login falhou ou algo inesperado aconteceu. Nenhuma mensagem de erro padrão encontrada.")
    else:
        print(f"URL atual: {current_url}. Verifique o resultado manualmente.")

    print("Teste de interação concluído.")

except Exception as e:
    print(f"Ocorreu um erro durante o teste: {e}")

finally:
    # --- Finalizar ---
    print("Fechando o navegador em 5 segundos...")
    time.sleep(5)
    driver.quit()