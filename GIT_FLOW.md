# Git Flow – Projeto Vizinhança Digital

## 1. Objetivo

Este documento registra o uso do Git Flow no desenvolvimento da aplicação web Vizinhança Digital.

O projeto foi desenvolvido como uma plataforma de fidelização para o comércio local, permitindo que comerciantes adicionem pontos para clientes e que clientes utilizem esses pontos para resgatar produtos.

## 2. Estrutura de branches

Durante a organização do projeto, foram utilizadas branches com funções diferentes:

### main

A branch `main` representa a versão principal e estável da aplicação. É nela que fica a versão final do projeto, pronta para entrega e publicação no Render.

### develop

A branch `develop` representa a área de desenvolvimento. Ela é usada para reunir funcionalidades antes de serem enviadas para a versão final.

### feature/documentacao-git-flow

A branch `feature/documentacao-git-flow` foi criada para documentar o processo de desenvolvimento, as etapas do projeto e a aplicação do Git Flow.

## 3. Fluxo aplicado

O fluxo utilizado foi:

1. A aplicação final foi mantida na branch `main`.
2. Foi criada a branch `develop` a partir da `main`.
3. Foi criada a branch `feature/documentacao-git-flow` a partir da `develop`.
4. A documentação do Git Flow e das etapas de construção foi adicionada na feature.
5. A feature foi mesclada na branch `develop`.
6. A branch `develop` foi mesclada na branch `main`.

## 4. Etapas de desenvolvimento do projeto

O desenvolvimento do Vizinhança Digital foi organizado em etapas semelhantes a sprints.

### Sprint 1 – Definição do problema e proposta

Nesta etapa, foi definido o problema principal: pequenos comércios locais têm dificuldade em fidelizar clientes e controlar benefícios de forma organizada.

A solução proposta foi uma aplicação web de fidelização por pontos.

### Sprint 2 – Levantamento de requisitos

Foram definidos os principais requisitos do sistema:

- cadastro de usuário;
- login;
- separação entre cliente e comerciante;
- dashboard do cliente;
- painel do comerciante;
- catálogo de produtos;
- carrinho;
- simulação de Pix;
- histórico de resgates;
- benefícios;
- mercados parceiros;
- adição de pontos pelo CPF.

### Sprint 3 – Estrutura do sistema

Foi criada a estrutura da aplicação utilizando Python, Flask, HTML, CSS e SQLite.

Também foram criadas as tabelas principais do banco de dados:

- usuarios;
- produtos;
- historico.

### Sprint 4 – Área do cliente

Foi desenvolvida a área do cliente, contendo:

- dashboard com pontos;
- catálogo de produtos;
- carrinho;
- resgate de produtos;
- histórico;
- perfil;
- benefícios;
- mercados parceiros.

### Sprint 5 – Área do comerciante

Foi desenvolvido o painel do comerciante, permitindo:

- visualizar clientes cadastrados;
- consultar produtos disponíveis;
- visualizar indicadores;
- adicionar pontos para clientes pelo CPF.

### Sprint 6 – Testes e correções

Foram feitos testes de login, cadastro, rotas, validação de CPF, redirecionamento por tipo de usuário, carrinho, Pix simulado, histórico e painel do comerciante.

Também foram corrigidos problemas visuais, botões de voltar, mensagens de erro e separação entre cliente e comerciante.

### Sprint 7 – Publicação

O projeto foi enviado para o GitHub e publicado no Render, tornando a aplicação acessível por meio de um link online.

## 5. Tecnologias utilizadas

- HTML;
- CSS;
- Python;
- Flask;
- SQLite;
- Git;
- GitHub;
- Render.

## 6. Links do projeto

Repositório GitHub:

https://github.com/monieslimelo/vizinhanca-digital

Aplicação publicada no Render:

https://vizinhanca-digital.onrender.com

## 7. Conclusão

O Git Flow foi utilizado para organizar o desenvolvimento e a entrega da aplicação web Vizinhança Digital.

A branch `main` representa a versão final e estável, a branch `develop` concentra o desenvolvimento e a branch `feature/documentacao-git-flow` registra a documentação da funcionalidade e das etapas de construção.

Esse fluxo ajuda a organizar o desenvolvimento, evitar alterações diretas na versão principal e demonstrar uma metodologia profissional de versionamento.