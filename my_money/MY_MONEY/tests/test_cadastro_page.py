import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configurações ---
# Especifique o caminho para o seu ChromeDriver se não estiver no PATH
# Exemplo: CHROME_DRIVER_PATH = '/caminho/para/seu/chromedriver'
CHROME_DRIVER_PATH = None  # Modifique se necessário

CADASTRO_URL = 'http://localhost:5000/cadastro' # Rota para a página de cadastro
LOGIN_URL = 'http://localhost:5000/login'
NEW_USER_EMAIL = 'teste@exemplo.com' # O e-mail usado no teste de login
NEW_USER_PASSWORD = 'senha123'       # A senha usada no teste de login

# --- Inicializar o WebDriver ---
if CHROME_DRIVER_PATH:
    service_obj = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service_obj)
else:
    driver = webdriver.Chrome()

driver.implicitly_wait(5)

try:
    print(f"Acessando a página de cadastro: {CADASTRO_URL}")
    driver.get(CADASTRO_URL)
    time.sleep(1)

    # --- Preencher o formulário de cadastro ---
    # O formulário em cadastro.html tem inputs com name="email" e name="senha"
    print(f"Preenchendo o campo de e-mail com: {NEW_USER_EMAIL}")
    email_field = driver.find_element(By.NAME, 'email')
    email_field.send_keys(NEW_USER_EMAIL)
    time.sleep(1)

    print(f"Preenchendo o campo de senha com: {NEW_USER_PASSWORD}")
    password_field = driver.find_element(By.NAME, 'senha')
    password_field.send_keys(NEW_USER_PASSWORD)
    time.sleep(1)

    # --- Clicar no botão de cadastrar ---
    # O botão em cadastro.html é <button type="submit" class="btn btn-primary w-100">Cadastrar</button>
    print("Clicando no botão 'Cadastrar'...")
    # Usando um seletor CSS mais específico para o botão dentro do formulário da página de cadastro
    cadastrar_button = driver.find_element(By.CSS_SELECTOR, 'form[action="/cadastro"] button[type="submit"]')
    cadastrar_button.click()
    time.sleep(2) # Aguardar o processamento e possível redirecionamento

    # --- Verificar o resultado ---
    current_url = driver.current_url

    # Cenário 1: Cadastro bem-sucedido -> Redirecionado para a página de login
    if LOGIN_URL in current_url:
        print("Redirecionado para a página de login. Verificando mensagem de sucesso...")
        # A mensagem flash de sucesso em cadastro.html é <div class="mt-2 text-success">{{ message }}</div>
        # A rota de cadastro em login.py envia "Usuário cadastrado com sucesso! Faça login."
        try:
            success_message_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-success"))
            )
            if success_message_element and "Usuário cadastrado com sucesso" in success_message_element.text:
                print(f"SUCESSO: Usuário '{NEW_USER_EMAIL}' cadastrado com sucesso! Mensagem: '{success_message_element.text}'")
            else:
                print("AVISO: Redirecionado para login, mas a mensagem de sucesso esperada não foi encontrada ou difere.")
        except Exception as e_msg:
            print(f"AVISO: Redirecionado para login, mas ocorreu um erro ao tentar encontrar a mensagem de sucesso: {e_msg}")

    # Cenário 2: Usuário já existe -> Permanece na página de cadastro (ou redireciona para ela) com mensagem de erro
    # A rota de cadastro em login.py envia "Usuário já existe. Tente outro email." com categoria 'danger'
    # A mensagem flash de erro em cadastro.html é <div class="mt-2 text-danger">{{ message }}</div>
    elif CADASTRO_URL in current_url:
        print("Permaneceu na página de cadastro. Verificando mensagem de erro (usuário já existe)...")
        try:
            error_message_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-danger"))
            )
            if error_message_element and "Usuário já existe" in error_message_element.text:
                print(f"INFO: O usuário '{NEW_USER_EMAIL}' já existe. Mensagem: '{error_message_element.text}'")
            else:
                print("AVISO: Permaneceu na página de cadastro, mas a mensagem de 'usuário já existe' esperada não foi encontrada ou difere.")
        except Exception as e_msg:
            print(f"AVISO: Permaneceu na página de cadastro, mas ocorreu um erro ao tentar encontrar a mensagem de erro: {e_msg}")
    else:
        print(f"URL inesperada após tentativa de cadastro: {current_url}. Verifique manualmente.")

    print("Teste de cadastro concluído.")

except Exception as e:
    print(f"Ocorreu um erro durante o teste de cadastro: {e}")

finally:
    print("Fechando o navegador em 5 segundos...")
    time.sleep(5)
    driver.quit()