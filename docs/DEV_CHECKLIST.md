# Hord Manager Development Checklist

## Recent Updates
- **Authentication System**: Complete login page with Player/GM roles (Demo: player123/gm123 passwords)
- **Metal Pricing**: Removed web scraping, using clean random generation within realistic ranges for 16 metals
- **Gemstone Pricing**: Added 20 common gemstones with fixed average pricing (no variation)
- **UI Improvements**: Password visibility toggle (5-second auto-hide), currencies displayed above metals
- **Steel Metal**: Added as 16th metal with kg units and proper conversion
- **Database Schema**: Fixed migration to include all required tables and columns
- **Gold-Only Display**: Modified UI to show only gold equivalent values, removed all USD pricing displays
- **Network Connectivity**: Resolved server connectivity issues, both backend and frontend running stable

## Core Architecture

- [x] Set up backend web server (FastAPI skeleton running)
- [x] Set up frontend framework (React, Vue, or Svelte) *(React with Vite, Material-UI, React Router)*
- [x] Implement user authentication (password-protected GM screen) *(Login page with Player/GM roles, localStorage persistence, 5-second password visibility toggle)*
- [x] Implement session management (track sessions globally) *(basic global session counter)*
- [x] Set up database (SQLite via SQLAlchemy) *(Fixed schema with all required tables and columns)*
- [x] Implement API for frontend-backend communication *(health, sessions, currencies CRUD, metals pricing API, gemstone pricing API)*
- [x] Database migration system *(Alembic with corrected initial migration including global_state table)*
- [x] Error handling and network connectivity *(Resolved server startup and connection issues)*

## Data Models

- [x] Player model
- [x] GM model (settings, inbox)
- [x] Currency model (name, denominations, value in oz gold)
- [x] Metal model (price history)
- [x] Gemstone model (name, value per carat, player holdings)
- [x] Art model (name, description, appraisal)
- [x] Real Estate model (name, location, appraisal, income)
- [x] Business model (ownership, investors, net worth)

## Metal Price Generation

- [x] Identify target website and data to extract (e.g., <https://www.dailymetalprice.com/metalpricescurr.php>) *(Replaced with random generation)*
- [x] ~~Send HTTP request to fetch HTML content~~ *(Removed web scraping)*
- [x] ~~Parse HTML content to locate relevant data (e.g., using BeautifulSoup)~~ *(Removed web scraping)*
- [x] Generate realistic metal prices for: Aluminum, Cobalt, Copper, Gold, Lead, Lithium, Molybdenum, Neodymium, Nickel, Palladium, Platinum, Silver, Steel, Tin, Uranium, Zinc *(Random generation within realistic ranges)*
- [x] Handle price variation and realistic ranges *(±10% variation within specified min/max bounds)*
- [x] Store extracted data in the database *(with session tracking and gold price conversion)*
- [x] Schedule or trigger price generation (on session increment or at regular intervals) *(automatic on session increment + manual API endpoint)*

## Gemstone Price Generation

- [x] Identify 20 common gemstones for pricing *(Diamond, Ruby, Sapphire, Emerald, Amethyst, Topaz, Garnet, Peridot, Citrine, Aquamarine, Tourmaline, Opal, Jade, Lapis Lazuli, Turquoise, Moonstone, Onyx, Carnelian, Jasper, Quartz)*
- [x] Generate fixed average pricing per carat *(Using (min_price + max_price) / 2 formula for consistency)*
- [x] Implement gemstone pricing API endpoints *(GET /gemstones/prices and /gemstones/current-prices)*
- [x] Display gemstones in UI with gold equivalent values *(Added to currencies page below metals section)*

## Currency & Value Conversion

- [x] Implement value conversion logic (oz gold as base unit) *(comprehensive conversion service with gold as base unit)*
- [x] Support for dollar and custom currencies *(USD + custom currencies with denominations)*
- [x] Support for precious metals (lb/oz/kg) and gemstones (carats) *(metal & gemstone value conversion endpoints, including Steel in kg units)*
- [x] Display denominations for each currency *(breakdown formatting with denomination display)*
- [x] USD to gold equivalent calculation *(1 USD = 1/gold_price_in_dollars oz gold)*
- [x] Real-time price variation *(random generation within realistic ranges for all 16 metals)*
- [x] Gemstone value conversion (carats to oz gold) *(Fixed average pricing for 20 gemstones)*
- [x] Gold-only display mode *(UI modified to show only gold equivalent values, USD columns removed)*

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

- [x] List all currencies and denominations *(USD Dollar with gold equivalent display)*
- [ ] Graph price of each currency over sessions (relative to oz gold)
- [x] List all metals and prices *(16 metals including Steel, with gold equivalent only - USD removed)*
- [ ] Graph price of each metal over sessions (relative to oz gold)
- [x] Display currencies section above metals section *(User-requested layout change)*
- [x] List all gemstones and prices *(20 gemstones with fixed average pricing, gold equivalent only)*
- [x] Three-section layout *(Currencies → Metals → Gemstones, all showing only gold equivalent values)*

## GM Screen (Password Protected)

- [ ] Add/edit currencies and denominations *(UI placeholder created)*
- [ ] Set currency values
- [x] Toggle visibility of dollar currency to players *(Complete: settings flag + endpoint + UI)*
- [x] Set exchange fee, interest rate, growth factor *(Complete: UI and backend integration)*
- [x] Set loan terms (interest, length, down payment, payment calc) *(Complete: Custom interest rates, terms, and payment calculations for each loan)*
- [ ] Add/edit gemstones and values *(UI placeholder created)*
- [ ] View all player net worths and breakdowns (pie/line graphs)
- [ ] View total player net worth and graphs
- [x] Session counter (increment, update all) *(Complete: UI with session increment and price updates)*
- [ ] Reset/delete all data (with confirm) *(UI structure created, backend implementation pending)*
- [x] Inbox (appraisals, business, investments, loans) *(Complete: Full inbox management system)*
  - [x] Appraisal requests (approve, set value) *(Complete: UI with value input for approvals)*
  - [x] Business approval (approve/disapprove, set income) *(Complete: UI with income setting)*
  - [x] Investment approval (approve/disapprove, update income) *(Complete: approve/reject functionality)*
  - [x] Loan petitions (approve/disapprove, set terms) *(Complete: approve/reject with response data)*

## Packaging & Deployment

- [ ] Package as .app image for Linux
- [ ] Package as .exe for Windows
- [ ] Ensure local network accessibility
- [ ] Test cross-platform compatibility

## Testing & QA

- [x] Unit tests for backend logic (health endpoint)
- [x] Manual API testing *(All endpoints functional: health, sessions, currencies, metals, gemstones)*
- [x] UI/UX testing *(Authentication flow, currency/metal/gemstone display, gold-only values)*
- [x] Database schema validation *(Migration fixes applied, all tables present)*
- [ ] Integration tests for API
- [ ] Data persistence and reset tests

## Documentation

- [ ] User guide
- [ ] GM guide
- [x] Developer setup guide (README environment & tooling)

---

**Legend:**

- [ ] Not started
- [x] Complete

Add notes and check off items as you progress.
