# Hord Manager Development Checklist

## Core Architecture
- [ ] Set up backend web server (Python/FastAPI or Node.js/Express)
- [ ] Set up frontend framework (React, Vue, or Svelte)
- [ ] Implement user authentication (password-protected GM screen)
- [ ] Implement session management (track sessions globally)
- [ ] Set up database (SQLite, PostgreSQL, or file-based for local use)
- [ ] Implement API for frontend-backend communication

## Data Models
- [ ] Player model (wealth, horde, bank, loans, businesses, net worth)
- [ ] GM model (settings, inbox, session counter)
- [ ] Currency model (name, denominations, value in oz gold)
- [ ] Metal model (name, value per oz/lb, inventory)
- [ ] Gemstone model (name, value per carat, inventory)
- [ ] Art/Real Estate/Business models

## Web Scraping
- [ ] Scrape metal prices from https://www.dailymetalprice.com/metalpricescurr.php
- [ ] Parse and store prices for: Aluminum, Cobalt, Copper, Gold, Lead, Molybdenum, Neodymium, Nickel, Palladium, Platinum, Silver, Tin, Uranium, Zinc
- [ ] Schedule regular scraping (on session increment or interval)

## Currency & Value Conversion
- [ ] Implement value conversion logic (oz gold as base unit)
- [ ] Support for dollar and custom currencies
- [ ] Support for precious metals (lb/oz) and gemstones (carats)
- [ ] Display denominations for each currency

## Player Pages
- [ ] Treasure Horde
  - [ ] Art category (add, appraise, request appraisal)
  - [ ] Gemstone category (add, display value per carat, total value)
  - [ ] Metals category (add, display value per oz/lb, total value)
  - [ ] Real estate (add, appraise, request appraisal)
- [ ] Banking
  - [ ] Bank account (deposit, withdraw, exchange fee)
  - [ ] Loan office (view, accept, petition, status, payments)
- [ ] Business
  - [ ] Start business (petition GM)
  - [ ] Invest in business (petition GM)
  - [ ] Display businesses (net worth, income per session)
- [ ] Net Worth
  - [ ] Breakdown by category/subcategory
  - [ ] Real estate breakdown
  - [ ] Business breakdown
  - [ ] Total net worth
  - [ ] Pie chart (category portions)
  - [ ] Line graph (net worth over sessions)

## Currency Page
- [ ] List all currencies and denominations
- [ ] Graph price of each currency over sessions (relative to oz gold)
- [ ] List all metals and prices
- [ ] Graph price of each metal over sessions (relative to oz gold)

## GM Screen (Password Protected)
- [ ] Add/edit currencies and denominations
- [ ] Set currency values
- [ ] Set exchange fee, interest rate, growth factor
- [ ] Set loan terms (interest, length, down payment, payment calc)
- [ ] Add/edit gemstones and values
- [ ] View all player net worths and breakdowns (pie/line graphs)
- [ ] View total player net worth and graphs
- [ ] Session counter (increment, update all)
- [ ] Reset/delete all data (with confirm)
- [ ] Inbox (appraisals, business, investments, loans)
  - [ ] Appraisal requests (approve, set value)
  - [ ] Business approval (approve/disapprove, set income)
  - [ ] Investment approval (approve/disapprove, update income)
  - [ ] Loan petitions (approve/disapprove, set terms)

## Packaging & Deployment
- [ ] Package as .app image for Linux
- [ ] Package as .exe for Windows
- [ ] Ensure local network accessibility
- [ ] Test cross-platform compatibility

## Testing & QA
- [ ] Unit tests for backend logic
- [ ] Integration tests for API
- [ ] UI/UX testing
- [ ] Data persistence and reset tests

## Documentation
- [ ] User guide
- [ ] GM guide
- [ ] Developer setup guide

---

**Legend:**
- [ ] Not started
- [x] Complete

Add notes and check off items as you progress.