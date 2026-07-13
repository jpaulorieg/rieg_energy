# Rieg Energy

## Objetivo

Desenvolver uma integração nativa para o Home Assistant denominada **Rieg Energy**.

A integração deverá ler informações de um banco PostgreSQL que já contém dados de energia solar, consumo elétrico, previsão do tempo e faturas de energia, transformando essas informações em sensores nativos do Home Assistant e importando estatísticas históricas utilizando a API oficial interna do Home Assistant.

A integração NÃO deve utilizar a API da Growatt.

Ela deve funcionar 100% sobre os dados existentes no PostgreSQL.

---

# Tecnologias

Python 3.13+

Home Assistant Core latest

asyncio

asyncpg

aiohttp

DataUpdateCoordinator

Config Flow

Diagnostics

Entity Registry

Statistics API

Long Term Statistics

Energy Dashboard

Quality Scale Gold

HACS Compatible

---

# Estrutura do projeto

Criar exatamente esta estrutura.

custom_components/
    rieg_energy/
        __init__.py
        manifest.json
        const.py
        config_flow.py
        coordinator.py
        api.py
        sensor.py
        statistics.py
        diagnostics.py
        services.py
        services.yaml
        icons.json
        strings.json
        translations/
            en.json
            pt-BR.json

tests/

.github/

README.md

LICENSE

pyproject.toml

requirements-dev.txt

---

# Configuração

A integração deverá possuir Config Flow.

Na tela de configuração solicitar:

Hostname PostgreSQL

Porta

Database

Usuário

Senha

SSL

Intervalo de atualização

Timezone

Após salvar, validar a conexão.

---

# Banco PostgreSQL

## hourly_producer

Campos

date_producer

hour_producer

minute_producer

complete_hour

quantitty_producer

Representa:

Potência instantânea em Watts.

A tabela recebe atualização a cada 15 minutos.

Gerar sensor:

sensor.solar_power

device_class:

power

unit_of_measurement:

W

state_class:

measurement

---

## monthly_producer

Campos

date_producer

quantitty_producer

Representa:

Energia produzida diariamente.

Valor em kWh.

Atualizada diariamente às 19:00.

Gerar sensor

sensor.energy_today

device_class:

energy

unit:

kWh

state_class:

total_increasing

Também gerar:

Energia semana

Energia mês

Energia ano

Energia total

---

## meteoblue.solar_weather

Criar sensores

Previsão geração

Radiação solar

Cobertura de nuvens

Sunshine Time

DNI

GHI

DIF

---

## fatura

Criar sensores

Valor da última conta

Mês referência

Data vencimento

---

## fatura_item

Gerar sensores

Preço médio do kWh

Energia TE

Energia TUSD

Bandeira tarifária

Valor injetado

Valor consumido

---

## fatura_leitura

Criar sensores

Energia consumida

Energia injetada

Leitura anterior

Leitura atual

Diferença entre leituras

---

# Coordinator

Utilizar DataUpdateCoordinator.

Atualização padrão:

300 segundos.

Não realizar consultas desnecessárias.

Utilizar cache.

---

# Statistics

Criar módulo statistics.py.

Utilizar exclusivamente as APIs oficiais internas do Home Assistant.

Não escrever diretamente no banco SQLite.

Importar estatísticas utilizando:

async_add_external_statistics

Importar:

Todo histórico da tabela monthly_producer.

Cada linha representa um dia.

Exemplo:

2024-01-01

12.3 kWh

↓

Registrar como estatística histórica.

O importador deve:

identificar registros já importados

continuar após interrupções

não duplicar dados

executar em lotes

registrar progresso

registrar erros

permitir reprocessamento

---

# Serviços

Criar serviços:

rieg_energy.import_history

Importa todo histórico.

rieg_energy.rebuild_statistics

Recria estatísticas.

rieg_energy.sync_now

Sincroniza imediatamente.

rieg_energy.clear_cache

Limpa cache.

---

# Diagnóstico

Implementar diagnostics.py

Exibir:

Versão

Quantidade de sensores

Última sincronização

Tempo médio consulta

Quantidade registros

Último erro

---

# Logging

Criar logger próprio.

Suportar níveis:

INFO

WARNING

ERROR

DEBUG

---

# Tratamento de erros

Reconexão automática PostgreSQL.

Timeout.

Retry exponencial.

Pool de conexões.

---

# Performance

Utilizar asyncpg.

Não utilizar psycopg2.

Utilizar pool.

Todas as consultas assíncronas.

---

# Qualidade

Todo código tipado.

Black

Ruff

Pytest

Mypy

---

# Testes

Criar testes para:

Conexão PostgreSQL

Coordinator

Sensores

Statistics

Services

Config Flow

---

# README

Criar documentação completa.

Instalação manual.

Instalação via HACS.

Configuração.

Exemplos.

Troubleshooting.

---

# Objetivo final

Após instalar a integração no Home Assistant, ela deverá:

Conectar ao PostgreSQL.

Criar automaticamente todas as entidades.

Importar todo histórico da geração solar.

Popular o Dashboard de Energia.

Atualizar automaticamente os sensores.

Permitir sincronização manual.

Ser compatível com HACS.

Seguir as recomendações oficiais do Home Assistant para integrações de qualidade Gold.