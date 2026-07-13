# Implementation Notes

## Observações sobre a especificação

O `SPECIFICATION.md` define completamente a estrutura do projeto e os requisitos técnicos principais. Já para algumas tabelas PostgreSQL (`meteoblue.solar_weather`, `fatura`, `fatura_item`, `fatura_leitura`), ele define os sensores esperados, mas não fixa explicitamente os nomes físicos de todas as colunas.

## Solução adotada

Para permanecer aderente às APIs oficiais do Home Assistant e não inventar persistência paralela:

- A integração consulta essas tabelas de forma assíncrona usando `asyncpg`.
- Os valores são normalizados por aliases de coluna em `api.py`.
- O importador histórico usa apenas `async_add_external_statistics`.
- O progresso do importador é salvo com `homeassistant.helpers.storage.Store`, sem escrever diretamente no banco do Home Assistant.

## Limitação conhecida

Caso o schema real do PostgreSQL use nomes de colunas diferentes dos aliases previstos, será necessário ajustar o mapeamento em `custom_components/rieg_energy/api.py`.

## Alternativa oficial adotada

Quando a API do Home Assistant não expõe um mecanismo estável para persistir checkpoints de importação dentro do `recorder`, a alternativa oficial mais aderente é usar `Store` para salvar o progresso da integração fora do banco do Home Assistant.
