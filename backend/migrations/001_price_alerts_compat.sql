-- ShopSphere price-alert compatibility migration.
-- Safe to run repeatedly against an existing local PostgreSQL volume.
ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS target_price DOUBLE PRECISION;
ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS min_price DOUBLE PRECISION;
ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS max_price DOUBLE PRECISION;
ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS last_notified_at TIMESTAMP;
ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS active BOOLEAN DEFAULT TRUE;
ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

UPDATE price_alerts
SET min_price = target_price
WHERE min_price IS NULL AND target_price IS NOT NULL;

UPDATE price_alerts
SET max_price = target_price
WHERE max_price IS NULL AND target_price IS NOT NULL;

UPDATE price_alerts
SET active = TRUE
WHERE active IS NULL;

UPDATE price_alerts
SET created_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL;
