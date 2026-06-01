# Trading Bot — Binance Futures Testnet

A simplified Python trading bot that places orders on the Binance Futures Testnet (USDT-M) with a clean CLI interface, structured code, and comprehensive logging.

## Features

- Place **MARKET**, **LIMIT**, and **STOP** (stop-limit) orders
- Support for **BUY** and **SELL** sides
- CLI powered by [Click](https://click.palletsprojects.com/) with input validation
- Structured project: separate API client layer, order logic, validators, and logging
- All API requests, responses, and errors logged to `logs/trading_bot.log`
- Exception handling for invalid inputs, API errors, and network failures
- Account info and leverage change commands included

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py           # Binance Futures API client (HMAC-SHA256 signing, REST)
│   ├── orders.py            # Order placement logic + response formatting
│   ├── validators.py        # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py    # Dual logger (file + console)
├── cli.py                   # Click CLI entry point
├── logs/                    # Log output directory
├── README.md
├── requirements.txt
└── .env.example
```

## Setup

### 1. Prerequisites

- Python 3.8+
- A Binance Futures Testnet account ([register here](https://testnet.binancefuture.com))

### 2. Get Testnet API Credentials

1. Go to [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Log in / register
3. Go to API Management and generate a new API key pair
4. Note down the **API Key** and **Secret Key**

### 3. Install Dependencies

```bash
cd trading_bot
pip install -r requirements.txt
```

### 4. Configure API Credentials

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
BINANCE_API_KEY=your_actual_api_key
BINANCE_SECRET_KEY=your_actual_secret_key
```

> **Never commit your `.env` file.** It is already in `.gitignore`.

## Usage

All commands are run from the `trading_bot` directory:

```bash
cd trading_bot
python cli.py --help
```

### Place a Market Order

```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Place a Limit Order

```bash
python cli.py order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 30000
```

### Place a Stop-Limit Order (Bonus)

```bash
python cli.py order --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --price 29000 --stop-price 29500
```

### Change Leverage

```bash
python cli.py leverage --symbol BTCUSDT --leverage 10
```

### View Account Info

```bash
python cli.py account
```

## Examples

### Market BUY Order Output

```
==================================================
   ORDER REQUEST SUMMARY
==================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
==================================================

==================================================
   ORDER RESPONSE
==================================================
  Order ID         : 123456789
  Symbol           : BTCUSDT
  Status           : NEW
  Side             : BUY
  Type             : MARKET
  Original Qty     : 0.001
  Executed Qty      : 0.001
  Avg Price        : 67500.00
==================================================

Order placed successfully!
```

### Limit SELL Order Output

```
==================================================
   ORDER REQUEST SUMMARY
==================================================
  Symbol     : BTCUSDT
  Side       : SELL
  Type       : LIMIT
  Quantity   : 0.001
  Price      : 70000
==================================================

==================================================
   ORDER RESPONSE
==================================================
  Order ID         : 123456790
  Symbol           : BTCUSDT
  Status           : NEW
  Side             : SELL
  Type             : LIMIT
  Original Qty     : 0.001
  Price            : 70000.00
  Time in Force    : GTC
==================================================

Order placed successfully!
```

## Logging

All operations are logged to `logs/trading_bot.log` with timestamps, including:

- API request details (endpoint, params)
- API responses (status, body)
- Validation errors
- Network/connection errors
- Order placements and results

## Error Handling

The bot handles the following error scenarios:

| Scenario | Behavior |
|---|---|
| Invalid symbol format | Clear validation error message |
| Missing price for LIMIT order | Prompts user that price is required |
| Missing stop-price for STOP order | Prompts user that stop-price is required |
| Invalid quantity (zero/negative) | Validation error with guidance |
| API authentication failure | Clear API key error message |
| Insufficient balance | Binance error code and message displayed |
| Network timeout/connection failure | Connection error with retry suggestion |

## Assumptions

- This bot targets the **Binance Futures Testnet** only (`https://testnet.binancefuture.com`). It is NOT for production trading.
- API credentials are loaded from environment variables via `.env` file (using `python-dotenv`).
- Quantity precision is not validated client-side — the Binance API will reject invalid precision. The user should check the exchange info for symbol-specific lot size filters.
- All orders use USDT-M (linear) contracts.
- The `STOP` order type maps to Binance's stop-limit order (requires both `stopPrice` and `price`).
- **Testnet Limitation**: STOP/conditional orders (STOP, STOP_MARKET, TAKE_PROFIT) return error `-4120` on the Binance Futures Testnet because it requires the Algo Order API which is not available on testnet. MARKET and LIMIT orders work perfectly. STOP orders are implemented in the code and will work on production Binance Futures.

## License

This project is built as part of the Primetrade.ai hiring assignment.