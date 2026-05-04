CREATE TABLE IF NOT EXISTS current_usage_raw(
    id BIGSERIAL PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL,
    period_from TIMESTAMPTZ NOT NULL,
    period_to TIMESTAMPTZ NOT NULL,
    call_timestamp TIMESTAMPTZ NOT NULL,
    last_update TIMESTAMPTZ NOT NULL,
    total_price NUMERIC(20, 10) NOT NULL,
    total_price_currency VARCHAR(10) NOT NULL,
    full_response_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS history_usage_raw (
    id BIGSERIAL PRIMARY KEY,
    usage_id VARCHAR(50),
    period_from TIMESTAMPTZ NOT NULL,
    period_to TIMESTAMPTZ NOT NULL,
    call_timestamp TIMESTAMPTZ NOT NULL,
    last_update TIMESTAMPTZ NOT NULL,
    total_price NUMERIC(20, 10) NOT NULL,
    total_price_currency VARCHAR(10) NOT NULL,
    full_response_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)