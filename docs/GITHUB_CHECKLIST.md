# GitHub Publishing Checklist

## Before the first push

- [ ] Extract the final ZIP and rename the project folder to `shopsphere`.
- [ ] Run `docker compose up -d --build` successfully.
- [ ] Open `http://localhost:5173`.
- [ ] Verify product search/filtering.
- [ ] Verify product details and the multi-retailer comparison section.
- [ ] Verify wishlist.
- [ ] Verify price history.
- [ ] Verify price alert creation and Price Alerts page.
- [ ] Verify `http://localhost:8000/api/health` returns `{"status":"ok",...}`.
- [ ] Confirm `.env` is not committed.
- [ ] Confirm no passwords/API keys are present in source files.

## Suggested repository name

`shopsphere-price-comparison`

## Suggested description

`Dockerized React + FastAPI + PostgreSQL price-comparison platform with multi-retailer offers, price history, alerts, authentication, and CI.`
