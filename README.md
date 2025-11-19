# Vinheria DevOps

Projeto de demonstração de arquitetura de microserviços para uma aplicação de e-commerce de vinhos, implementando práticas de DevOps com Docker, nginx e Jenkins.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Serviços](#serviços)
- [Pré-requisitos](#pré-requisitos)
- [Como Executar](#como-executar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Endpoints da API](#endpoints-da-api)
- [CI/CD](#cicd)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)

## 🍷 Sobre o Projeto

Este projeto implementa uma arquitetura de microserviços para uma aplicação de vinhos (Vinheria), demonstrando conceitos de DevOps, containerização e orquestração de serviços. A aplicação é composta por três microserviços principais (Autenticação, Inventário e Pedidos), gerenciados através de um reverse proxy nginx com suporte a SSL/TLS.

## 🏗️ Arquitetura

```
┌─────────────────┐
│   Cliente       │
└────────┬────────┘
         │ HTTPS (443)
         ▼
┌─────────────────┐
│   nginx         │  (Reverse Proxy / Gateway)
│   (Porta 80/443)│
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬─────────────┐
    │         │              │             │
    ▼         ▼              ▼             ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐
│  Auth  │ │Inventory │ │  Order   │ │ Jenkins │
│ :8080  │ │  :5001   │ │  :5000   │ │  :8085  │
└────────┘ └──────────┘ └──────────┘ └─────────┘
```

### Características da Arquitetura

- **Gateway Pattern**: nginx atua como único ponto de entrada
- **Service Discovery**: Comunicação entre serviços via nomes de host Docker
- **SSL/TLS**: Redirecionamento automático HTTP → HTTPS
- **Isolamento**: Cada serviço em container separado com rede dedicada
- **Autenticação JWT**: Proteção de endpoints com tokens JWT para acesso externo
- **Service-to-Service**: Comunicação interna entre serviços sem necessidade de autenticação

## 🔧 Serviços

### 1. Auth Service (`auth`)
Serviço de autenticação que gera tokens JWT para os usuários.

- **Porta**: 8080 (externa), 8080 (interna)
- **Tecnologia**: Flask (Python)
- **Funcionalidade**: Validação de credenciais e geração de tokens JWT

### 2. Inventory Service (`inventory-service`)
Serviço responsável por gerenciar o inventário de produtos.

- **Porta**: 5001 (externa não exposta, apenas interna)
- **Tecnologia**: Flask (Python)
- **Funcionalidade**: Verificação de disponibilidade de itens
- **Autenticação**: Requer token JWT para acesso externo (via nginx)
- **Comunicação Interna**: Permite chamadas service-to-service sem autenticação

### 3. Order Service (`order-service`)
Serviço de processamento de pedidos que se comunica com o Inventory Service.

- **Porta**: 5000 (externa não exposta, apenas interna)
- **Tecnologia**: Flask (Python)
- **Funcionalidade**: Criação de pedidos com verificação de estoque
- **Autenticação**: Requer token JWT para acesso externo (via nginx)
- **Dependência**: Requer Inventory Service em execução

### 4. nginx
Reverse proxy e gateway da aplicação.

- **Portas**: 80 (HTTP), 443 (HTTPS)
- **Funcionalidades**:
  - Redirecionamento HTTP → HTTPS
  - Roteamento de requisições para os microserviços
  - Terminação SSL/TLS

### 5. Jenkins
Servidor de CI/CD para automação de builds e deploys.

- **Porta**: 8085 (Web UI), 50000 (Agent)
- **Funcionalidade**: Pipeline de build e deploy automatizado

## 📦 Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 1.29 ou superior)

Para verificar as instalações:

```bash
docker --version
docker-compose --version
```

### Certificados SSL/TLS

O projeto requer certificados SSL/TLS na pasta `certs/`. Você precisa ter os seguintes arquivos:

- `fullchain.pem` - Certificado completo
- `privkey.pem` - Chave privada

**Nota**: Se você não possui certificados, pode gerar certificados auto-assinados para desenvolvimento:

```bash
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/privkey.pem \
  -out certs/fullchain.pem \
  -subj "/CN=localhost"
```

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd vinheria-devops
```

### 2. Configure os certificados SSL

Certifique-se de que os certificados estão na pasta `certs/` (veja seção de pré-requisitos).

### 3. Inicie os serviços

```bash
docker-compose up -d
```

Este comando irá:
- Construir as imagens dos serviços (auth, inventory-service, order-service)
- Criar a rede Docker `vinheria_net`
- Iniciar todos os containers

### 4. Verifique o status dos serviços

```bash
docker-compose ps
```

### 5. Visualize os logs

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f auth
docker-compose logs -f nginx
```

### 6. Parar os serviços

```bash
docker-compose down
```

Para remover também os volumes (incluindo dados do Jenkins):

```bash
docker-compose down -v
```

## 📁 Estrutura do Projeto

```
vinheria-devops/
├── auth/
│   ├── app.py              # Aplicação Flask do serviço de autenticação
│   └── Dockerfile          # Imagem Docker do auth service
├── inventory-service/
│   ├── app.py              # Aplicação Flask do serviço de inventário
│   └── Dockerfile          # Imagem Docker do inventory service
├── order-service/
│   ├── app.py              # Aplicação Flask do serviço de pedidos
│   └── Dockerfile          # Imagem Docker do order service
├── nginx/
│   └── nginx.conf          # Configuração do nginx (reverse proxy)
├── jenkins/
│   └── Jenkinsfile         # Pipeline de CI/CD
├── certs/                  # Certificados SSL/TLS
│   ├── fullchain.pem
│   └── privkey.pem
├── docker-compose.yml      # Orquestração dos serviços
└── README.md              # Este arquivo
```

## 🔌 Endpoints da API

### Autenticação

**POST** `/auth/login`
- **Descrição**: Realiza login e retorna token JWT
- **Body**:
  ```json
  {
    "username": "admin",
    "password": "password"
  }
  ```
- **Resposta de Sucesso** (200):
  ```json
  {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
  ```
- **Resposta de Erro** (401):
  ```json
  {
    "error": "credenciais inválidas"
  }
  ```

### Inventário

**GET** `/inventory/check`
- **Descrição**: Verifica disponibilidade de item no inventário
- **Autenticação**: Requerida (token JWT no header `Authorization`)
- **Headers**:
  ```
  Authorization: Bearer <token_jwt>
  ```
- **Resposta de Sucesso** (200):
  ```json
  {
    "item_id": "Vinho-001",
    "available": true,
    "service": "InventoryService",
    "message": "Item is available.",
    "user": "admin"
  }
  ```
- **Resposta de Erro** (401):
  ```json
  {
    "error": "Token de autenticação não fornecido"
  }
  ```
  ou
  ```json
  {
    "error": "Token expirado"
  }
  ```

### Pedidos

**POST** `/orders/create`
- **Descrição**: Cria um novo pedido (verifica estoque automaticamente)
- **Autenticação**: Requerida (token JWT no header `Authorization`)
- **Headers**:
  ```
  Authorization: Bearer <token_jwt>
  ```
- **Resposta de Sucesso** (201):
  ```json
  {
    "status": "Order Created",
    "inventory_check": {
      "item_id": "Vinho-001",
      "available": true,
      "service": "InventoryService",
      "message": "Item is available.",
      "user": "internal_service"
    },
    "message": "Order processed and inventory confirmed.",
    "user": "admin"
  }
  ```
- **Resposta de Erro** (400/401/503):
  ```json
  {
    "status": "Failed",
    "message": "Inventory check failed or item unavailable."
  }
  ```
  ou (401):
  ```json
  {
    "error": "Token de autenticação não fornecido"
  }
  ```

### Exemplos de Uso

#### 1. Login (obter token JWT)
```bash
curl -X POST https://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  -k
```

**Resposta esperada:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 2. Verificar Inventário (com autenticação)
```bash
# Primeiro, obtenha o token (veja exemplo acima)
TOKEN="seu_token_aqui"

curl -X GET https://localhost/inventory/check \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

#### 3. Criar Pedido (com autenticação)
```bash
# Primeiro, obtenha o token (veja exemplo acima)
TOKEN="seu_token_aqui"

curl -X POST https://localhost/orders/create \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

#### Exemplo Completo (script bash)
```bash
#!/bin/bash

# 1. Fazer login e obter token
TOKEN=$(curl -s -X POST https://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  -k | jq -r '.token')

echo "Token obtido: ${TOKEN:0:20}..."

# 2. Verificar inventário
echo "Verificando inventário..."
curl -X GET https://localhost/inventory/check \
  -H "Authorization: Bearer $TOKEN" \
  -k

# 3. Criar pedido
echo -e "\nCriando pedido..."
curl -X POST https://localhost/orders/create \
  -H "Authorization: Bearer $TOKEN" \
  -k
```

**Nota**: O flag `-k` é necessário para ignorar erros de certificado SSL auto-assinado em desenvolvimento.

## 🔄 CI/CD

O projeto inclui um pipeline Jenkins configurado para automatizar o processo de build e deploy.

### Acessar Jenkins

1. Inicie os serviços: `docker-compose up -d`
2. Acesse: `http://localhost:8085`
3. Obtenha a senha inicial do administrador:
   ```bash
   docker exec vin_jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```

### Pipeline

O pipeline definido em `jenkins/Jenkinsfile` inclui as seguintes etapas:

1. **Checkout**: Simulação de checkout do código
2. **Build**: Build dos serviços Docker
3. **Publish**: Publicação dos artefatos

Para executar o pipeline, configure um job no Jenkins apontando para o `Jenkinsfile`.

## 🛠️ Tecnologias Utilizadas

- **Python 3.9**: Linguagem de programação dos microserviços
- **Flask**: Framework web para os serviços
- **Docker**: Containerização dos serviços
- **Docker Compose**: Orquestração de containers
- **nginx**: Reverse proxy e gateway
- **Jenkins**: Automação de CI/CD
- **JWT (PyJWT)**: Autenticação baseada em tokens
- **SSL/TLS**: Comunicação segura

## 🔐 Segurança

### Autenticação JWT

O projeto implementa autenticação baseada em tokens JWT:

- **Geração de Tokens**: O serviço `auth` gera tokens JWT após validação de credenciais
- **Validação de Tokens**: Os serviços `inventory-service` e `order-service` validam tokens JWT para acesso externo
- **Expiração**: Tokens expiram após 15 minutos
- **Service-to-Service**: Comunicação interna entre serviços usa header `X-Internal-Service` para bypass de autenticação

### Variáveis de Ambiente

Todos os serviços que validam tokens utilizam a variável de ambiente `JWT_SECRET` para verificar a assinatura dos tokens JWT. Em produção, certifique-se de:

1. Usar uma chave secreta forte e única
2. Não commitar chaves no repositório
3. Utilizar um gerenciador de segredos (ex: Docker Secrets, HashiCorp Vault)
4. Usar a mesma chave secreta em todos os serviços que validam tokens

### Credenciais Padrão

⚠️ **ATENÇÃO**: As credenciais padrão (`admin`/`password`) são apenas para desenvolvimento. Em produção, implemente:

- Autenticação robusta
- Hash de senhas (bcrypt, argon2)
- Integração com banco de dados
- Rate limiting
- Validação de entrada
- Refresh tokens para renovação de sessão
- Revogação de tokens

### Proteção de Endpoints

- **Endpoints Protegidos**: `/inventory/check` e `/orders/create` requerem autenticação JWT
- **Endpoints Públicos**: `/auth/login` é o único endpoint público
- **Comunicação Interna**: Serviços podem se comunicar internamente sem autenticação usando header especial

## 🐛 Troubleshooting

### Serviços não iniciam

```bash
# Verifique os logs
docker-compose logs

# Verifique se as portas estão disponíveis
netstat -tulpn | grep -E '80|443|8080|8085|5000|5001'
```

### Erro de certificado SSL

Certifique-se de que os arquivos `fullchain.pem` e `privkey.pem` estão na pasta `certs/`.

### Serviços não se comunicam

Verifique se todos os serviços estão na mesma rede Docker:

```bash
docker network inspect vinheria-devops_vinheria_net
```

### Jenkins não acessível

Verifique se o container está rodando e se a porta 8085 está disponível:

```bash
docker ps | grep jenkins
docker-compose logs jenkins
```

## 📝 Licença

Este projeto é uma demonstração educacional e pode ser usado livremente para fins de aprendizado.

## 👥 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

**Desenvolvido com ❤️ para demonstração de práticas DevOps**

