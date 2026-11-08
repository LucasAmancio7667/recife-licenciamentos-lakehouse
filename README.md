# Recife Licenciamentos Lakehouse

Lakehouse com **arquitetura medalhão** (landing → bronze → silver → gold) construído no **Databricks** com **PySpark** e **Delta Lake**, a partir dos dados abertos da Prefeitura do Recife sobre licenciamentos e cadastro de empresas.

> **Status:** em andamento. Exploração dos dados concluída; camada bronze em construção.

## Objetivo

Cruzar os licenciamentos **urbanístico**, **ambiental** e **sanitário** com o cadastro de **empresas da cidade**, usando o CNPJ como chave, para responder perguntas como:

- Quais empresas possuem mais de um tipo de licença?
- Como se distribuem os licenciamentos por bairro e por atividade econômica (CNAE)?
- Qual a situação (ativa ou inativa) das empresas licenciadas?

*(Ajustar as perguntas conforme a gold ficar pronta.)*

## Fontes de dados

Portal de Dados Abertos do Recife (dados.recife.pe.gov.br), licença **ODbL**:

| Dataset | Colunas |
|---|---|
| Licenciamento urbanístico | 33 |
| Licenciamento ambiental | 33 |
| Licenciamento sanitário | 33 |
| Empresas da cidade do Recife (ativas e inativas) | 22 |

Os três licenciamentos compartilham a mesma estrutura. Os arquivos CSV **não** estão neste repositório; baixe-os na fonte.

## Arquitetura

```
landing (CSV no volume, como baixado)
   └─► bronze  (Delta; tudo string + colunas de controle)
          └─► silver (tipos, deduplicação, padronização, LGPD)
                 └─► gold (tabelas analíticas)
```

| Camada | O que faz | Status |
|---|---|---|
| Landing | Arquivos originais em um volume do Unity Catalog | pronto |
| Bronze | Leitura sem limpeza, tudo como string, com colunas de controle | em andamento |
| Silver | Tipagem, dedup, padronização, tratamento de dados pessoais | a fazer |
| Gold | Tabelas para análise | a fazer |

## Dificuldades e achados

O que deu trabalho nos dados e como foi resolvido:

1. **CSV fora do padrão.** O separador é `;` e cada linha vem entre aspas, com aspas duplicadas dentro. A leitura inicial devolvia **1 coluna**. Resolvido com `sep=";"` e `escape='"'`, que levou a **33 colunas**.
2. **Caractere invisível (BOM)** no nome da primeira coluna, o que atrapalha a gravação em Delta. Os nomes de coluna são limpos antes de gravar.
3. **Formatos locais:** decimais com vírgula, datas em `AAAA-MM-DD` e valores vazios lidos como `null`.
4. **CNPJ ausente.** Muitos registros de obra (principalmente no urbanístico) não têm CNPJ e não podem ser ligados ao cadastro de empresas.
5. **Dados pessoais (LGPD).** Há identificadores mascarados (`33*****`) para pessoas físicas no cadastro de empresas, e em parte dos licenciamentos o CPF aparece no fim da razão social (MEI). Esses casos são excluídos ou mascarados.
6. **Duplicatas.** O cadastro de empresas tem 861.627 linhas, mas só 255.954 CNPJs distintos (cerca de 3,4 linhas por CNPJ), e 7.290 linhas são cópias exatas. Na silver será definida uma regra para uma linha por empresa.
7. **Ativas e inativas sobrepostas.** 736 CNPJs aparecem nas duas listas; será definida uma regra de desempate (por exemplo, pela data de encerramento).
8. **Erro que virou aprendizado:** um `join` sem chave gerou um produto cartesiano (mais de 4 trilhões de linhas). A chave sempre vai explícita, e valido a ordem de grandeza do resultado antes de seguir.

## Cruzamento entre as bases

- **31.391** CNPJs distintos nos três licenciamentos juntos. **5.322** aparecem nos três tipos ao mesmo tempo.
- Cruzando com as empresas **ativas**, só 22.884 tinham correspondência. Ao incluir as **inativas**, o total sobe para **29.968 (95,5%)**: a maior parte dos "faltantes" eram empresas que já fecharam.
- Os **1.423** CNPJs (4,5%) sem correspondência se dividem em: pessoas físicas/MEI (293), filiais (145) e matrizes comuns (1.111). Hipótese para estas últimas: empresas cadastradas fora do município. Fica como **limitação conhecida**, sinalizada na silver pela coluna `situacao_cadastro`.

## Estrutura do repositório

```
├── README.md
├── docs/
├── notebooks/
└── src/
```

## Tecnologias

Databricks (Unity Catalog, volumes) · PySpark · Delta Lake · Python

## Licenças

- Código: MIT.
- Dados: ODbL, conforme o Portal de Dados Abertos do Recife.

## Autor

**Lucas Amancio** · [LinkedIn](https://www.linkedin.com/) · [GitHub](https://github.com/)
