# Documentação da API

## Endpoints Gerais

| Método | URL           | Descrição                             |
|--------|---------------|-------------------------------------|
| POST   | /           | Rota raiz (sucess)                   |
| POST   | /login/     | Autenticação (delegado ao app auth) |
| POST   | /admin      | Interface administrativa do Django  |
| POST   | /api/token  | Obtenção de token de autenticação   |

---

## App: Authenticator

| Método | URL          | Descrição                  |
|--------|--------------|----------------------------|
| POST   | /auth      | Login e autenticação       |

---

## App: Get Empresas

| Método | URL                  | Descrição                          |
|--------|----------------------|----------------------------------|
| POST   | /empresa/listar    | Listar empresas                   |
| POST   | /empresa/faturamento | Obter faturamentos das empresas   |
| POST   | /empresa/contrato  | Contratos das empresas            |
| POST   | /empresa/socios    | Sócios das empresas               |
| POST   | /empresa/novos     | Novos clientes no mês             |
| POST   | /empresa/cadastro  | Cadastro das empresas             |
| POST   | /empresa/aniversariantes | Sócios aniversariantes          |

---

## App: Get Folha

| Método | URL                 | Descrição                      |
|--------|---------------------|-------------------------------|
| POST   | /folha/empregados | Listar empregados             |
| POST   | /folha/contadores | Listar contadores             |

---

## App: Get Main Pages

| Método | URL                     | Descrição                       |
|--------|-------------------------|--------------------------------|
| POST   | /main/cliente          | Análise do cliente              |
| POST   | /main/usuario          | Análise de usuários            |
| POST   | /main/usuario/modulo   | Análise de usuários por módulo |

---

## App: Get Usuarios

| Método | URL                              | Descrição                               |
|--------|---------------------------------|-----------------------------------------|
| POST   | /usuarios/listar               | Listar usuários                        |
| POST   | /usuarios/atividades/empresa  | Atividades dos usuários por cliente   |
| POST   | /usuarios/atividades/modulo   | Atividades dos usuários por módulo    |
| POST   | /usuarios/atividades/total    | Total de atividades dos usuários      |
| POST   | /usuarios/importacoes/usuario | Importações por usuário                |
| POST   | /usuarios/importacoes/empresa | Importações por empresa                |
| POST   | /usuarios/lancamentos/usuario | Lançamentos por usuário                |
| POST   | /usuarios/lancamentos/empresa | Lançamentos por empresa                |
| POST   | /usuarios/lancamentos/manual  | Lançamentos manuais                    |

---

# Observações

- A maioria dos endpoints utiliza o método POST.
- A autenticação e permissões não estão detalhadas aqui.
- URLs são relativas ao domínio base da aplicação.