# Rieg Energy - Roadmap

> Roadmap oficial do projeto **Rieg Energy**, uma integração nativa para o Home Assistant voltada ao monitoramento de geração solar, previsão meteorológica, leituras energéticas e dados financeiros a partir de PostgreSQL.

---

# Status das versões

| Versão | Status |
|--------|--------|
| 0.1.0 | Concluída |
| 0.2.0 | Parcialmente concluída |
| 0.3.0 | Parcialmente concluída |
| 0.4.0 | Parcialmente concluída |
| 1.0.0 | Em andamento |

---

# Versão 0.1.0 - Fundação

## Funcionalidades

- [x] Estrutura inicial da integração
- [x] Configuração via interface
- [x] Pool PostgreSQL
- [x] Atualização assíncrona
- [x] Tratamento de erros
- [x] Diagnostics
- [x] Compatibilidade com Home Assistant
- [x] Testes automatizados iniciais

---

# Versão 0.2.0 - Sensores

## Produção Solar

- [x] `sensor.solar_power`
- [x] `sensor.energy_today`
- [x] `sensor.energy_week`
- [x] `sensor.energy_month`
- [x] `sensor.energy_year`
- [x] `sensor.energy_total`

## Faturas

- [x] `sensor.last_bill`
- [x] `sensor.bill_due_date`
- [x] `sensor.reference_month`

## Leitura do Medidor

- [x] `sensor.energy_consumed`
- [x] `sensor.energy_injected`
- [x] `sensor.previous_reading`
- [x] `sensor.current_reading`
- [x] `sensor.reading_difference`

## Custos

- [x] `sensor.average_price`
- [x] `sensor.energy_te`
- [x] `sensor.energy_tusd`
- [x] `sensor.injected_value`
- [x] `sensor.consumed_value`
- [x] `sensor.tariff_flag`

## Previsão Solar

- [x] `sensor.forecast_generation`
- [x] `sensor.solar_radiation`
- [x] `sensor.sunshine_time`
- [x] `sensor.cloud_cover`
- [x] `sensor.dni`
- [x] `sensor.ghi`
- [x] `sensor.dif`

---

# Versão 0.3.0 - Dashboard de Energia

## Integração Energy Dashboard

- [x] Produção solar histórica
- [ ] Consumo
- [ ] Energia injetada
- [ ] Energia recebida
- [ ] Autoconsumo
- [ ] Autossuficiência

---

# Versão 0.4.0 - Estatísticas Históricas

## Importação

- [x] Importação completa de `monthly_producer`
- [x] Importação incremental
- [x] Reprocessamento
- [x] Continuação automática
- [x] Detecção de duplicidade por checkpoint
- [x] Processamento em lote

## Serviços

- [x] `import_history`
- [x] `rebuild_statistics`
- [x] `sync_now`
- [x] `clear_cache`
- [ ] `clear_statistics`

---

# Publicação e Qualidade

## Repositório

- [x] Compatibilidade HACS
- [x] Workflow de CI
- [x] Workflow de release
- [x] Workflow Hassfest
- [x] Documentação base
- [x] Changelog
- [x] Guia de contribuição
- [x] Pasta `docs/`

## Qualidade Técnica

- [ ] Ruff executado com sucesso no ambiente local desta revisão
- [ ] Black executado com sucesso no ambiente local desta revisão
- [ ] MyPy executado com sucesso no ambiente local desta revisão
- [ ] Pytest executado com sucesso no ambiente local desta revisão
- [ ] Cobertura validada com mínimo de 95%

---

# Pendências Relevantes

- Modelagem completa do Energy Dashboard além de produção
- Validação real da suíte de qualidade após instalação das dependências
- Cobertura comprovada em CI com publicação de relatório
- Ajuste fino dos aliases de colunas conforme schema real do PostgreSQL
