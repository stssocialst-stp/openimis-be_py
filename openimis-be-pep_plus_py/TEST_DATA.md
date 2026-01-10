# PEP+ Test Data Seeding

Este documento explica como usar a migration de dados de teste do módulo PEP+.

## Visão Geral

A migration `0013_seed_test_data.py` cria dados de teste completos para todas as ferramentas PEP+, permitindo que desenvolvedores e testadorestenham um ambiente funcional imediatamente após a instalação.

## Como Ativar

### Opção 1: Variável de Ambiente (Recomendado)

Defina a variável de ambiente `FEED_DATA=true` antes de rodar as migrations:

```bash
# Linux/Mac
export FEED_DATA=true
python manage.py migrate pep_plus

# Windows (CMD)
set FEED_DATA=true
python manage.py migrate pep_plus

# Windows (PowerShell)
$env:FEED_DATA="true"
python manage.py migrate pep_plus

# Docker Compose
docker-compose exec backend bash -c "FEED_DATA=true python manage.py migrate pep_plus"
```

### Opção 2: Arquivo .env

Adicione ao arquivo `.env`:

```env
FEED_DATA=true
```

Depois rode as migrations normalmente:

```bash
python manage.py migrate pep_plus
```

## Comportamento Padrão

**IMPORTANTE:** Se `FEED_DATA` não estiver definido ou for `false`, a migration **NÃO criará nenhum dado de teste**. Isso garante que ambientes de produção não sejam poluídos com dados fictícios.

Valores aceitos como `true`:
- `true`
- `1`
- `yes`

Qualquer outro valor (incluindo ausência da variável) é considerado `false`.

## Dados Criados

A migration cria dados de teste na seguinte ordem:

### 1. Usuários (core_User)
- `coord_distrital_test` - Coordenador Distrital
- `coord_nacional_test` - Coordenador Nacional
- `tecnico_social_test` - Técnico Social
- `tecnico_admin_test` - Técnico Administrativo
- `formador_test` - Formador
- `supervisor_test` - Supervisor

### 2. Localizações (Location)
**Distritos:**
- `test_distrito_1` - Distrito Teste 1
- `test_distrito_2` - Distrito Teste 2

**Localidades:**
- `test_localidade_1` - Localidade Teste 1
- `test_localidade_2` - Localidade Teste 2
- `test_localidade_3` - Localidade Teste 3

### 3. Módulos Educacionais
- `TEST_M01` - Módulo 1: Eu Como Cuidador
- `TEST_M02` - Módulo 2: Rotinas Diárias
- `TEST_M03` - Módulo 3: Dimensão Afetiva
- `TEST_M04` - Módulo 4: Desenvolvimento Integral
- `TEST_M05` - Módulo 5: Conversar e Aprender

### 4. Grupos Familiares
- `TEST_GF001` - Grupo Familiar Teste 1 (15 famílias)
- `TEST_GF002` - Grupo Familiar Teste 2 (12 famílias)
- `TEST_GF003` - Grupo Familiar Teste 3 (18 famílias)

### 5. Sessões PEP (Ferramenta 1)
- `TEST_SESS001` - Sessão de teste para Módulo 1
- `TEST_SESS002` - Sessão de teste para Módulo 2
- `TEST_SESS003` - Sessão de teste para Módulo 3

### 6. Execução de Sessão (Ferramenta 3)
- 1 execução de sessão vinculada a `TEST_SESS001`
- Inclui práticas positivas e auto-avaliação

### 7. Supervisão de Sessão (Ferramenta 4)
- 1 supervisão de sessão vinculada a `TEST_SESS001`
- Inclui avaliações e feedback

### 8. Relatório Distrital Bimestral (Ferramenta 5)
- 1 relatório para `test_distrito_1` - Bimestre 1
- Inclui estatísticas e dados de técnicos

### 9. Roteiro de Reunião Bimestral (Ferramenta 6)
- 1 agenda de reunião
- Inclui resumo da agenda e plano de ação

### 10. Relatório de Supervisão Bimestral (Ferramenta 7)
- 1 relatório de supervisão para `test_distrito_1`
- Inclui avaliações de técnicos e notas de sessões PEP

## Testando GraphQL API

Após rodar a migration com `FEED_DATA=true`, você pode testar as queries:

```graphql
# Listar usuários de teste
query {
  users(username_Icontains: "test") {
    edges {
      node {
        id
        username
      }
    }
  }
}

# Listar grupos familiares de teste
query {
  gruposFamiliares(codigo_Istartswith: "TEST_GF") {
    edges {
      node {
        id
        codigo
        nome
        numeroFamilias
      }
    }
  }
}

# Listar sessões PEP de teste
query {
  sessoesPep(codigoSessao_Istartswith: "TEST_SESS") {
    edges {
      node {
        id
        codigoSessao
        nomeModulo
        dataSessao
        status
      }
    }
  }
}

# Listar relatórios distritais de teste
query {
  relatoriosDistritais(distrito_Code: "test_distrito_1") {
    edges {
      node {
        id
        periodo
        ano
        numeroSessoesConduzidas
        numeroFamiliasAtendidas
      }
    }
  }
}
```

## Removendo Dados de Teste

Para remover todos os dados de teste:

```bash
# Certifique-se que FEED_DATA=true está definido
export FEED_DATA=true

# Reverta a migration
python manage.py migrate pep_plus 0012_add_resumo_da_agenda_field

# E aplique novamente (sem dados de teste)
unset FEED_DATA
python manage.py migrate pep_plus
```

## Proteção de Produção

A migration verifica `FEED_DATA` em **TODAS as operações**, incluindo reverse. Isso significa:

- ✅ Se `FEED_DATA=false` (ou não definido), a migration não faz nada
- ✅ Se `FEED_DATA=true`, a migration cria/remove dados de teste
- ✅ Ambiente de produção permanece seguro mesmo se a migration for executada

## Checklist de Desenvolvimento

Use este checklist ao testar o módulo PEP+:

- [ ] Defina `FEED_DATA=true` no `.env` ou export
- [ ] Execute `python manage.py migrate pep_plus`
- [ ] Verifique no Django Admin que os dados foram criados:
  - [ ] Usuários de teste existem
  - [ ] Localizações de teste existem
  - [ ] Grupos familiares existem
  - [ ] Sessões PEP existem
- [ ] Teste as queries GraphQL acima
- [ ] Teste as mutations usando os IDs dos dados de teste
- [ ] Ao finalizar testes, remova dados com migrate reverso

## Logs de Execução

A migration imprime logs informativos:

```
[PEP+ Seed] Creating test users...
[PEP+ Seed] Created 6 test users
[PEP+ Seed] Creating test locations...
[PEP+ Seed] Created 2 districts and 3 localities
[PEP+ Seed] Creating educational modules...
[PEP+ Seed] Created 5 educational modules
...
```

Se `FEED_DATA` não estiver ativo:

```
[PEP+ Seed] Skipping user seed - FEED_DATA not set to true
[PEP+ Seed] Skipping location seed - FEED_DATA not set to true
...
```

## Idempotência

A migration é **idempotente**: pode ser executada múltiplas vezes sem criar dados duplicados. Ela verifica se dados de teste já existem antes de criar novos.

## Troubleshooting

**Problema:** Migration não cria dados mesmo com `FEED_DATA=true`

**Solução:** Verifique se:
1. A variável está realmente definida: `echo $FEED_DATA`
2. O valor é exatamente `true`, `1`, ou `yes`
3. Os dados já não existem no banco (migration é idempotente)

**Problema:** Erro de Foreign Key ao criar dados

**Solução:** Certifique-se que as migrations dos módulos `core` e `location` foram executadas primeiro:
```bash
python manage.py migrate core
python manage.py migrate location
python manage.py migrate pep_plus
```

**Problema:** Quero recriar os dados de teste do zero

**Solução:**
```bash
# 1. Remova os dados existentes
export FEED_DATA=true
python manage.py migrate pep_plus 0012

# 2. Recrie os dados
python manage.py migrate pep_plus
```

## Ambiente Docker

No `docker-compose.yml`, adicione:

```yaml
services:
  backend:
    environment:
      - FEED_DATA=true  # Apenas para desenvolvimento!
```

Ou no `docker-compose-dev.yml`:

```yaml
services:
  backend:
    env_file:
      - .env.dev
```

E no `.env.dev`:
```
FEED_DATA=true
```

**⚠️ NUNCA defina `FEED_DATA=true` em ambientes de produção!**
