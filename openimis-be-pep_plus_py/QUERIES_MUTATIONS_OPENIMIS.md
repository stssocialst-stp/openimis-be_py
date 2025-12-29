# Queries e Mutations do openIMIS para PEP+

Este documento lista todas as queries e mutations disponíveis no openIMIS para buscar dados de **Distrito**, **Coordenador Distrital** e **Técnico Social**.

---

## 1. DISTRITO (Location)

### Queries Disponíveis:

#### `locations`
Busca localizações com filtros e ordenação.

```graphql
query {
  locations(
    orderBy: ["name"]
    code: "D001"
    type: "D"  # R=Region, D=District, W=Ward, V=Village
  ) {
    edges {
      node {
        id
        uuid
        code
        name
        type
        malePopulation
        femalePopulation
        otherPopulation
        families
        parent {
          id
          code
          name
        }
      }
    }
  }
}
```

**Filtros disponíveis:**
- `code` - Código da localização
- `name` - Nome da localização
- `type` - Tipo (R, D, W, V)
- `parent` - Localização pai
- `uuid` - UUID da localização

---

#### `locationsAll`
Retorna todas as localizações válidas sem filtros de permissão.

```graphql
query {
  locationsAll {
    edges {
      node {
        id
        uuid
        code
        name
        type
      }
    }
  }
}
```

---

#### `locationsStr`
Busca localizações por texto (código ou nome).

```graphql
query {
  locationsStr(str: "Maputo") {
    edges {
      node {
        id
        code
        name
        type
      }
    }
  }
}
```

**Parâmetros:**
- `str` - Busca parcial em código OU nome (case insensitive)

---

#### `userDistricts`
Retorna os distritos atribuídos ao usuário logado.

```graphql
query {
  userDistricts {
    id
    userUuid
    location {
      id
      uuid
      code
      name
      type
    }
    validityFrom
    validityTo
  }
}
```

**Nota:** Requer autenticação e funciona apenas para InteractiveUser.

---

#### `officerLocations`
Retorna localizações atribuídas a um oficial de inscrição.

```graphql
query {
  officerLocations(
    officerCode: "OFF001"
    locationType: "D"
  ) {
    id
    code
    name
    type
  }
}
```

**Parâmetros:**
- `officerCode` (obrigatório) - Código do oficial
- `locationType` (opcional) - Filtrar por tipo de localização

---

#### `validateLocationCode`
Valida se um código de localização é único.

```graphql
query {
  validateLocationCode(locationCode: "D005")
}
```

**Retorna:** `true` se único, `false` se já existe

---

### Mutations Disponíveis:

#### `createLocation`
Cria uma nova localização.

```graphql
mutation {
  createLocation(input: {
    code: "D005"
    name: "Distrito Novo"
    type: "D"
    parentUuid: "uuid-region"
    malePopulation: 50000
    femalePopulation: 52000
  }) {
    internalId
    clientMutationId
  }
}
```

---

#### `updateLocation`
Atualiza uma localização existente.

```graphql
mutation {
  updateLocation(input: {
    uuid: "location-uuid"
    name: "Distrito Atualizado"
    malePopulation: 51000
  }) {
    internalId
    clientMutationId
  }
}
```

---

#### `deleteLocation`
Remove uma localização (soft delete).

```graphql
mutation {
  deleteLocation(input: {
    uuids: ["location-uuid"]
  }) {
    internalId
    clientMutationId
  }
}
```

---

#### `moveLocation`
Move uma localização para outro pai.

```graphql
mutation {
  moveLocation(input: {
    uuid: "location-uuid"
    newParentUuid: "new-parent-uuid"
  }) {
    internalId
    clientMutationId
  }
}
```

---

## 2. COORDENADOR DISTRITAL E TÉCNICO SOCIAL (User)

### Queries Disponíveis:

#### `users`
Busca usuários com filtros extensivos.

```graphql
query {
  users(
    lastName: "Silva"
    otherNames: "João"
    roleId: 5
    districtId: 10
    userTypes: [INTERACTIVE]
    showHistory: false
  ) {
    edges {
      node {
        id
        uuid
        username
        lastName
        otherNames
        email
        phone
        birthDate
        language {
          code
          name
        }
        iUser {
          id
          lastLogin
          email
          healthFacility {
            id
            code
            name
          }
        }
        userDistricts {
          location {
            id
            code
            name
          }
        }
      }
    }
  }
}
```

**Filtros disponíveis:**
- `lastName` - Sobrenome (busca parcial, case insensitive)
- `otherNames` - Outros nomes (busca parcial, case insensitive)
- `phone` - Telefone (busca exata)
- `email` - Email (busca exata)
- `roleId` - ID da função (role)
- `roles` - Lista de IDs de funções
- `healthFacilityId` - ID da unidade de saúde base
- `regionId` - ID da região
- `regionIds` - Lista de IDs de regiões
- `districtId` - ID do distrito
- `municipalityId` - ID do município
- `villageId` - ID da aldeia
- `birthDateFrom` - Data de nascimento de
- `birthDateTo` - Data de nascimento até
- `userTypes` - Tipos de usuário: `INTERACTIVE`, `TECHNICAL`, `OFFICER`, `CLAIM_ADMIN`
- `language` - Código do idioma
- `showHistory` - Mostrar histórico
- `showDeleted` - Mostrar deletados
- `str` - Busca de texto em username, lastName, otherNames, email
- `parentLocation` - UUID da localização pai
- `parentLocationLevel` - Nível da localização pai

---

#### `interactiveUsers`
Busca apenas usuários interativos (com login).

```graphql
query {
  interactiveUsers(
    orderBy: ["lastName", "otherNames"]
    showHistory: false
  ) {
    edges {
      node {
        id
        uuid
        username
        lastName
        otherNames
        email
        lastLogin
        healthFacility {
          id
          code
          name
          location {
            id
            name
          }
        }
      }
    }
  }
}
```

**Filtros disponíveis:**
- `orderBy` - Lista de campos para ordenação
- `validity` - Data de validade
- `showHistory` - Mostrar histórico
- `clientMutationId` - ID da mutação do cliente

---

#### `user`
Retorna o usuário autenticado atual.

```graphql
query {
  user {
    id
    username
    lastName
    otherNames
    email
    language {
      code
      name
    }
  }
}
```

**Nota:** Sem parâmetros, retorna o usuário logado.

---

#### `enrolmentOfficers`
Busca oficiais de inscrição.

```graphql
query {
  enrolmentOfficers(
    str: "Silva"
  ) {
    edges {
      node {
        id
        uuid
        code
        lastName
        otherNames
        phone
        email
        officerVillages {
          id
          location {
            code
            name
          }
        }
      }
    }
  }
}
```

**Parâmetros:**
- `str` - Busca em código, lastName, otherNames, email

---

#### `validateUsername`
Valida se um username é único.

```graphql
query {
  validateUsername(username: "joao.silva")
}
```

**Retorna:** `true` se único, `false` se já existe

---

#### `validateUserEmail`
Valida se um email de usuário é único.

```graphql
query {
  validateUserEmail(userEmail: "joao@example.com")
}
```

**Retorna:** `true` se único, `false` se já existe

---

#### `usernameLength`
Retorna o tamanho mínimo/máximo para username.

```graphql
query {
  usernameLength
}
```

**Retorna:** Número inteiro

---

#### `passwordPolicy`
Retorna a política de senha configurada.

```graphql
query {
  passwordPolicy
}
```

**Retorna:**
```json
{
  "min_length": 8,
  "require_upper_case": 1,
  "require_lower_case": 1,
  "require_numbers": 1,
  "require_special_characters": 1
}
```

---

### Mutations Disponíveis:

#### `createUser`
Cria um novo usuário.

```graphql
mutation {
  createUser(input: {
    username: "joao.silva"
    lastName: "Silva"
    otherNames: "João Pedro"
    email: "joao@example.com"
    phone: "+258 84 1234567"
    birthDate: "1990-05-15"
    roleIds: [5, 8]
    districtIds: [10, 15]
    password: "SecureP@ss123"
    language: "pt"
  }) {
    internalId
    clientMutationId
  }
}
```

**Campos do input:**
- `username` (obrigatório)
- `lastName` (obrigatório)
- `otherNames` (obrigatório)
- `email`
- `phone`
- `birthDate`
- `roleIds` - Lista de IDs de roles
- `districtIds` - Lista de IDs de distritos
- `password` (obrigatório)
- `language` - Código do idioma

---

#### `updateUser`
Atualiza um usuário existente.

```graphql
mutation {
  updateUser(input: {
    uuid: "user-uuid"
    lastName: "Silva Santos"
    email: "joao.santos@example.com"
    phone: "+258 84 9876543"
  }) {
    internalId
    clientMutationId
  }
}
```

---

#### `deleteUser`
Remove um usuário (soft delete).

```graphql
mutation {
  deleteUser(input: {
    uuids: ["user-uuid"]
  }) {
    internalId
    clientMutationId
  }
}
```

---

#### `changeUserLanguage`
Altera o idioma do usuário.

```graphql
mutation {
  changeUserLanguage(input: {
    language: "en"
  }) {
    internalId
    clientMutationId
  }
}
```

---

#### `changePassword`
Altera a senha do usuário logado.

```graphql
mutation {
  changePassword(input: {
    oldPassword: "OldPass123"
    newPassword: "NewSecureP@ss456"
  }) {
    internalId
    clientMutationId
  }
}
```

---

#### `resetPassword`
Reseta a senha de um usuário (admin).

```graphql
mutation {
  resetPassword(input: {
    username: "joao.silva"
  }) {
    internalId
    clientMutationId
  }
}
```

---

#### `setPassword`
Define uma nova senha para um usuário.

```graphql
mutation {
  setPassword(input: {
    username: "joao.silva"
    password: "NewP@ssword789"
  }) {
    internalId
    clientMutationId
  }
}
```

---

## 3. EXEMPLOS DE USO NO PEP+

### Exemplo 1: Buscar distritos para dropdown

```graphql
query GetDistricts {
  locations(type: "D", orderBy: ["name"]) {
    edges {
      node {
        id
        uuid
        code
        name
      }
    }
  }
}
```

---

### Exemplo 2: Buscar coordenadores distritais

```graphql
query GetDistrictCoordinators {
  users(
    roleId: 5  # ID da role "Coordenador Distrital"
    userTypes: [INTERACTIVE]
    districtId: 10
  ) {
    edges {
      node {
        id
        uuid
        username
        lastName
        otherNames
        email
        phone
      }
    }
  }
}
```

---

### Exemplo 3: Buscar técnicos sociais por distrito

```graphql
query GetSocialTechnicians($districtId: Int!) {
  users(
    roleId: 8  # ID da role "Técnico Social"
    districtId: $districtId
    userTypes: [INTERACTIVE]
  ) {
    edges {
      node {
        id
        uuid
        username
        lastName
        otherNames
        email
        phone
        userDistricts {
          location {
            code
            name
          }
        }
      }
    }
  }
}
```

---

### Exemplo 4: Buscar usuários com busca de texto

```graphql
query SearchUsers($searchText: String!) {
  users(str: $searchText) {
    edges {
      node {
        id
        uuid
        username
        lastName
        otherNames
        email
      }
    }
  }
}
```

---

## 4. NOTAS IMPORTANTES

### Permissões

Todas as queries e mutations requerem autenticação e permissões específicas:
- **Location queries**: `gql_query_locations_perms`
- **User queries**: `gql_query_users_perms`
- **User mutations**: `gql_mutation_users_perms`

### Row Security

O openIMIS implementa **Row-Level Security** que limita automaticamente os resultados baseado nas permissões do usuário logado:
- Usuários veem apenas dados dos distritos atribuídos a eles
- Superusuários veem todos os dados

### Paginação

Todas as queries usam **Relay Cursor-based Pagination**:

```graphql
query {
  users(first: 10, after: "cursor-string") {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      cursor
      node {
        id
        username
      }
    }
  }
}
```

### IDs vs UUIDs

- **ID**: Inteiro sequencial do banco de dados
- **UUID**: Identificador único global (string)
- Use UUID para referências em mutations
- Use ID para filtros em queries (quando disponível)

---

## 5. REFERÊNCIAS

- Módulo Location: `/usr/local/lib/python3.11/site-packages/location/schema.py`
- Módulo Core: `/usr/local/lib/python3.11/site-packages/core/schema.py`
- Documentação GraphQL openIMIS: `GraphQL.md`
