# PEP+ Testing Environment Setup

Este documento explica como configurar um ambiente de teste funcional para o módulo PEP+.

## Problema Comum: "relation tblUsers does not exist"

Este erro ocorre quando você tenta rodar migrations em um banco de dados completamente vazio. O openIMIS requer um schema base antes das migrations poderem ser executadas.

## Solução: Inicialização Correta do Ambiente

### Opção 1: Usar Banco SQL Pré-configurado (Recomendado)

O openIMIS fornece dumps SQL com o schema e dados base já configurados:

```bash
# 1. Clone o repositório de banco de dados
git clone https://github.com/openimis/database_postgresql

# 2. Entre no diretório
cd database_postgresql

# 3. Concatene os arquivos SQL
bash concatenate_files.sh

# 4. Crie o banco de dados
createdb imis

# 5. Importe o schema completo
psql -d imis -a -f output/fullDemoDatabase.sql

# 6. Agora rode as migrations do PEP+
cd /path/to/openimis-be_py
export FEED_DATA=true  # Para criar dados de teste
python openIMIS/manage.py migrate pep_plus
```

### Opção 2: Migrations Sequenciais

Se você precisa criar um banco do zero:

```bash
# 1. Certifique-se que SCHEDULER_AUTOSTART está desativado
export SCHEDULER_AUTOSTART=false

# 2. Rode migrations na ordem correta
python openIMIS/manage.py migrate auth
python openIMIS/manage.py migrate contenttypes
python openIMIS/manage.py migrate sessions
python openIMIS/manage.py migrate admin
python openIMIS/manage.py migrate core
python openIMIS/manage.py migrate location
python openIMIS/manage.py migrate insuree
python openIMIS/manage.py migrate product
python openIMIS/manage.py migrate policy
python openIMIS/manage.py migrate claim
python openIMIS/manage.py migrate individual
python openIMIS/manage.py migrate pep_plus

# 3. Crie um superusuário
python openIMIS/manage.py createsuperuser

# 4. (Opcional) Popule dados de teste do PEP+
export FEED_DATA=true
python openIMIS/manage.py migrate pep_plus
```

### Opção 3: Docker Compose (Ambiente Completo)

Use o docker-compose para ambiente de desenvolvimento completo:

```bash
# 1. Clone o repositório principal
git clone https://github.com/openimis/openimis-be_py
cd openimis-be_py

# 2. Copie e configure o .env
cp .env.example .env

# Edite .env e configure:
# DB_HOST=db
# DB_PORT=5432
# DB_NAME=imis
# DB_USER=imis
# DB_PASSWORD=imis
# FEED_DATA=true  # Para dados de teste PEP+

# 3. Inicie os containers
docker-compose up -d

# 4. Execute as migrations
docker-compose exec backend python manage.py migrate

# 5. Crie superusuário
docker-compose exec backend python manage.py createsuperuser

# 6. Acesse o sistema
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api
# Django Admin: http://localhost:8000/admin
```

## Configurando Dados de Teste PEP+

A migration `0013_seed_test_data.py` cria automaticamente dados de teste completos, mas **APENAS** se a variável `FEED_DATA=true` estiver definida.

### Ativando Dados de Teste

```bash
# Opção 1: Variável de ambiente temporária
export FEED_DATA=true
python openIMIS/manage.py migrate pep_plus

# Opção 2: No arquivo .env
echo "FEED_DATA=true" >> .env
python openIMIS/manage.py migrate pep_plus

# Opção 3: Docker Compose
docker-compose exec -e FEED_DATA=true backend python manage.py migrate pep_plus
```

### O que é Criado

Com `FEED_DATA=true`, a migration cria:

- ✅ 6 usuários de teste (coordenadores, técnicos, formadores, supervisores)
- ✅ 2 distritos e 3 localidades de teste
- ✅ 5 módulos educacionais
- ✅ 3 grupos familiares
- ✅ 3 sessões PEP
- ✅ 1 execução de sessão, 1 supervisão, 3 relatórios

### Verificando Dados Criados

```bash
# Via Django Admin
# Acesse: http://localhost:8000/admin/
# Navegue para: PEP_PLUS > Módulos Educacionais / Grupos Familiares / etc.

# Via GraphQL
# Acesse: http://localhost:8000/api/graphql
# Query de exemplo:
query {
  gruposFamiliares(codigo_Istartswith: "TEST_GF") {
    edges {
      node {
        id
        codigo
        nome
      }
    }
  }
}
```

## Troubleshooting

### Erro: "relation tblUsers does not exist"

**Causa:** Banco de dados vazio, sem schema base do openIMIS.

**Solução:** Use a Opção 1 (Banco SQL Pré-configurado) ou rode as migrations na ordem correta (Opção 2).

### Erro: "django_apscheduler_djangojob does not exist"

**Causa:** O scheduler está tentando iniciar antes das migrations terminarem.

**Solução:**
```bash
export SCHEDULER_AUTOSTART=false
python openIMIS/manage.py migrate
```

### Erro: "Could not modify config: No such file or directory: 'openimis.json'"

**Causa:** O arquivo `openimis.json` não está no diretório esperado.

**Solução:**
```bash
# Copie o arquivo de exemplo
cp openimis.json.example openimis.json

# Ou crie um mínimo funcional
cat > openimis.json << 'EOF'
{
  "modules": [
    {"name": "core"},
    {"name": "location"},
    {"name": "individual"},
    {"name": "pep_plus"}
  ]
}
EOF
```

### Migration PEP+ Falha com LookupError

**Causa:** A migration `0013_seed_test_data.py` está tentando acessar modelos que ainda não existem.

**Solução:** A migration foi atualizada para ser resiliente e apenas avisar quando modelos não estão disponíveis. Certifique-se de ter a versão mais recente:

```bash
git pull origin feature/pep-plus-module
python openIMIS/manage.py migrate pep_plus
```

### Remover Dados de Teste

```bash
export FEED_DATA=true
python openIMIS/manage.py migrate pep_plus 0012_add_resumo_da_agenda_field
```

## Checklist de Setup Completo

- [ ] Banco de dados PostgreSQL rodando
- [ ] Schema base do openIMIS importado (via SQL dump ou migrations)
- [ ] Arquivo `openimis.json` configurado
- [ ] Arquivo `.env` configurado com credenciais do banco
- [ ] `SCHEDULER_AUTOSTART=false` durante migrations
- [ ] Migrations executadas: `python manage.py migrate`
- [ ] Superusuário criado: `python manage.py createsuperuser`
- [ ] (Opcional) `FEED_DATA=true` para dados de teste PEP+
- [ ] Django Admin acessível: http://localhost:8000/admin
- [ ] GraphQL API acessível: http://localhost:8000/api/graphql

## Próximos Passos

Após o setup bem-sucedido:

1. **Acesse o Django Admin** para verificar os dados criados
2. **Teste as GraphQL queries** no endpoint `/api/graphql`
3. **Leia TEST_DATA.md** para queries de exemplo
4. **Leia API_DOCUMENTATION.md** para referência completa da API

## Suporte

Se encontrar problemas:

1. Verifique os logs do backend: `docker-compose logs backend`
2. Verifique se todas as variáveis de ambiente estão corretas
3. Certifique-se que o banco de dados tem o schema base
4. Reporte issues em: https://github.com/openimis/openimis-be_py/issues
