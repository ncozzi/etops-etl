WITH deduplicated AS (

    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY transaction_id
                ORDER BY rowid
            ) AS row_num
        FROM {{ source('raw', 'raw_transaction_data') }}
    )
    WHERE row_num = 1

),

standardized AS (

    SELECT
        transaction_id,
        source_system,
        client_id,
        client_name,

        CASE
            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN ('switzerland', 'swiss', 'schweiz', 'suisse', 'ch')
                THEN 'CH'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN ('austria', 'österreich', 'oesterreich', 'at')
                THEN 'AT'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN ('germany', 'deutschland', 'ger', 'de')
                THEN 'DE'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN ('france', 'fr')
                THEN 'FR'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN ('luxembourg', 'lu')
                THEN 'LU'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN ('liechtenstein', 'li')
                THEN 'LI'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN (
                    'great britain',
                    'england',
                    'uk',
                    'u k',
                    'united kingdom',
                    'gb'
                )
                THEN 'GB'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN ('italy', 'italia', 'it')
                THEN 'IT'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN ('singapore', 'sg')
                THEN 'SG'

            WHEN LOWER(TRIM(REPLACE(CAST(client_country AS TEXT), '.', '')))
                IN (
                    'u s a',
                    'us',
                    'usa',
                    'united states',
                    'united states of america'
                )
                THEN 'US'

            ELSE NULL
        END AS client_country,

        CASE
            WHEN LOWER(TRIM(CAST(risk_profile AS TEXT))) LIKE 'ag%'
                THEN 'aggressive'

            WHEN LOWER(TRIM(CAST(risk_profile AS TEXT))) LIKE 'ba%'
                THEN 'balanced'

            WHEN LOWER(TRIM(CAST(risk_profile AS TEXT))) LIKE 'co%'
                THEN 'conservative'

            WHEN LOWER(TRIM(CAST(risk_profile AS TEXT))) LIKE 'gr%'
                THEN 'growth'

            ELSE NULL
        END AS risk_profile,

        advisor_id,
        advisor_name,
        channel,
        portfolio_id,
        transaction_date,
        
        CASE
            WHEN LOWER(TRIM(CAST(asset_class AS TEXT))) IN ('exchange traded fund', 'etf', 'eq', 'equtiy', 'equity')
                THEN 'Equity'
            WHEN LOWER(TRIM(CAST(asset_class AS TEXT))) IN ('stocks', 'eq')
                THEN 'Equity'
            WHEN LOWER(TRIM(CAST(asset_class AS TEXT))) IN ('bond', 'bnd', 'fixed income')
                THEN 'Fixed Income'
            WHEN LOWER(TRIM(CAST(asset_class AS TEXT))) IN ('fund', 'mutual fund')
                THEN 'Fund'
            WHEN LOWER(TRIM(CAST(asset_class AS TEXT))) IN ('cash', 'money market')
                THEN 'Cash'
            WHEN LOWER(TRIM(CAST(asset_class AS TEXT))) IN ('real estate', 'realestate', 'property')
                THEN 'Real Estate'
            WHEN LOWER(TRIM(CAST(asset_class AS TEXT))) IN ('crypto', 'cryptocurrency')
                THEN 'Crypto'
            WHEN LOWER(TRIM(CAST(asset_class AS TEXT))) IN ('commodity', 'commodities')
                THEN 'Commodity'
            ELSE NULL
        END AS asset_class,

        instrument_name,
        isin,

        CASE
            WHEN LOWER(TRIM(CAST(transaction_type AS TEXT))) IN ('buy', 'b')
                THEN 'buy'

            WHEN LOWER(TRIM(CAST(transaction_type AS TEXT))) IN ('sell', 's')
                THEN 'sell'

            WHEN LOWER(TRIM(CAST(transaction_type AS TEXT))) = 'dividend'
                THEN 'dividend'

            WHEN LOWER(TRIM(CAST(transaction_type AS TEXT))) = 'deposit'
                THEN 'deposit'

            WHEN LOWER(TRIM(CAST(transaction_type AS TEXT))) = 'withdrawal'
                THEN 'withdrawal'

            ELSE NULL
        END AS transaction_type,

        CAST(quantity AS REAL) AS quantity,
        CAST(price_per_unit AS REAL) AS price_per_unit,

        CASE
            WHEN LOWER(TRIM(CAST(currency AS TEXT))) IN ('chf', 'fr', 'fr.', 'sfr')
                THEN 'CHF'

            WHEN LOWER(TRIM(CAST(currency AS TEXT))) IN ('eur', 'euro')
                THEN 'EUR'

            WHEN LOWER(TRIM(CAST(currency AS TEXT))) = 'gbp'
                THEN 'GBP'

            WHEN LOWER(TRIM(CAST(currency AS TEXT))) IN ('usd', 'us dollar')
                THEN 'USD'

            ELSE NULL
        END AS currency,

        CAST(gross_amount AS REAL) AS gross_amount,
        CAST(fee AS REAL) AS fee,

        CASE
            WHEN LOWER(TRIM(CAST(fee_currency AS TEXT))) IN ('chf', 'fr', 'fr.', 'sfr')
                THEN 'CHF'

            WHEN LOWER(TRIM(CAST(fee_currency AS TEXT))) IN ('eur', 'euro')
                THEN 'EUR'

            WHEN LOWER(TRIM(CAST(fee_currency AS TEXT))) = 'gbp'
                THEN 'GBP'

            WHEN LOWER(TRIM(CAST(fee_currency AS TEXT))) IN ('usd', 'us dollar')
                THEN 'USD'

            ELSE NULL
        END AS fee_currency,

        deduplicated.status AS status,
        notes

    FROM deduplicated
),

with_fx AS (

    SELECT
        *,
        
        CASE
            WHEN currency = 'CHF' THEN 1.00
            WHEN currency = 'EUR' THEN 0.90
            WHEN currency = 'USD' THEN 0.85
            WHEN currency = 'GBP' THEN 1.08
            ELSE NULL
        END AS currency_fx_rate,

        CASE
            WHEN fee_currency = 'CHF' THEN 1.00
            WHEN fee_currency = 'EUR' THEN 0.90
            WHEN fee_currency = 'USD' THEN 0.85
            WHEN fee_currency = 'GBP' THEN 1.08
            ELSE NULL
        END AS fee_currency_fx_rate,

        CAST(gross_amount AS REAL) *
        CASE
            WHEN currency = 'CHF' THEN 1.00
            WHEN currency = 'EUR' THEN 0.90
            WHEN currency = 'USD' THEN 0.85
            WHEN currency = 'GBP' THEN 1.08
            ELSE NULL
        END AS gross_amount_chf,

        CAST(fee AS REAL) *
        CASE
            WHEN fee_currency = 'CHF' THEN 1.00
            WHEN fee_currency = 'EUR' THEN 0.90
            WHEN fee_currency = 'USD' THEN 0.85
            WHEN fee_currency = 'GBP' THEN 1.08
            ELSE NULL
        END AS fee_chf

    FROM standardized
)

SELECT *
FROM with_fx
