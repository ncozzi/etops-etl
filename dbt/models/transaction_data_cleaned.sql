WITH deduplicated AS (

    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY transaction_id
                ORDER BY rowid
            ) AS row_num
        FROM {{ source('raw', 'transaction_data') }}
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
    asset_class,
    instrument_name,
    isin,
    transaction_type,
    quantity,
    price_per_unit,
    currency,
    gross_amount,
    fee,
    fee_currency,
    deduplicated.status,
    notes

    FROM deduplicated
)

SELECT *
FROM standardized