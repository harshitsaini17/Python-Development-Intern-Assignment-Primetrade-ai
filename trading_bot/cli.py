import os
import sys

import click
from dotenv import load_dotenv

from bot.client import BinanceFuturesClient, BinanceAPIError, BinanceConnectionError
from bot.orders import OrderManager, format_order_summary, format_order_response
from bot.validators import ValidationError
from bot.logging_config import setup_logger

load_dotenv()

logger = setup_logger("trading_bot.cli")


@click.group()
def cli():
    """Binance Futures Testnet Trading Bot — CLI"""
    pass


@cli.command()
@click.option("--symbol", required=True, help="Trading pair symbol (e.g., BTCUSDT)")
@click.option("--side", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side")
@click.option("--type", "order_type", required=True, type=click.Choice(["MARKET", "LIMIT", "STOP"], case_sensitive=False), help="Order type")
@click.option("--quantity", required=True, help="Order quantity")
@click.option("--price", default=None, help="Limit price (required for LIMIT and STOP orders)")
@click.option("--stop-price", default=None, help="Stop price (required for STOP orders)")
@click.option("--time-in-force", default="GTC", help="Time in force (default: GTC)")
def order(symbol, side, order_type, quantity, price, stop_price, time_in_force):
    """Place an order on Binance Futures Testnet."""

    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")

    if not api_key or not secret_key:
        click.echo(click.style("ERROR: BINANCE_API_KEY and BINANCE_SECRET_KEY must be set.", fg="red"))
        click.echo("Set them in a .env file or as environment variables.")
        sys.exit(1)

    click.echo(format_order_summary(
        symbol=symbol, side=side, order_type=order_type,
        quantity=quantity, price=price, stop_price=stop_price,
    ))

    client = BinanceFuturesClient(api_key=api_key, secret_key=secret_key)
    manager = OrderManager(client)

    try:
        response = manager.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            time_in_force=time_in_force,
        )
        click.echo(format_order_response(response))
        click.echo(click.style("\nOrder placed successfully!", fg="green"))
    except ValidationError as e:
        click.echo(click.style(f"\nValidation Error: {e}", fg="red"))
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except BinanceAPIError as e:
        click.echo(click.style(f"\nAPI Error: {e}", fg="red"))
        logger.error(f"API error: {e}")
        sys.exit(1)
    except BinanceConnectionError as e:
        click.echo(click.style(f"\nConnection Error: {e}", fg="red"))
        logger.error(f"Connection error: {e}")
        sys.exit(1)


@cli.command()
def account():
    """Show account information from Binance Futures Testnet."""

    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")

    if not api_key or not secret_key:
        click.echo(click.style("ERROR: BINANCE_API_KEY and BINANCE_SECRET_KEY must be set.", fg="red"))
        sys.exit(1)

    client = BinanceFuturesClient(api_key=api_key, secret_key=secret_key)

    try:
        info = client.get_account_info()
        click.echo("=" * 50)
        click.echo("   ACCOUNT INFORMATION")
        click.echo("=" * 50)
        click.echo(f"  Total Wallet Balance : {info.get('totalWalletBalance', 'N/A')}")
        click.echo(f"  Available Balance    : {info.get('availableBalance', 'N/A')}")
        click.echo(f"  Unrealized PnL       : {info.get('totalUnrealizedProfit', 'N/A')}")
        click.echo(f"  Margin Balance       : {info.get('totalMarginBalance', 'N/A')}")
        click.echo("=" * 50)
    except (BinanceAPIError, BinanceConnectionError) as e:
        click.echo(click.style(f"\nError: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option("--symbol", required=True, help="Trading pair symbol (e.g., BTCUSDT)")
@click.option("--leverage", required=True, type=int, help="Leverage (1-125)")
def leverage(symbol, leverage):
    """Change leverage for a symbol on Binance Futures Testnet."""

    api_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_SECRET_KEY")

    if not api_key or not secret_key:
        click.echo(click.style("ERROR: BINANCE_API_KEY and BINANCE_SECRET_KEY must be set.", fg="red"))
        sys.exit(1)

    if not 1 <= leverage <= 125:
        click.echo(click.style("Leverage must be between 1 and 125.", fg="red"))
        sys.exit(1)

    client = BinanceFuturesClient(api_key=api_key, secret_key=secret_key)

    try:
        response = client.change_leverage(symbol=symbol.upper(), leverage=leverage)
        click.echo(click.style(f"Leverage for {symbol} set to {leverage}x", fg="green"))
        logger.info(f"Leverage changed: {response}")
    except (BinanceAPIError, BinanceConnectionError) as e:
        click.echo(click.style(f"\nError: {e}", fg="red"))
        sys.exit(1)


if __name__ == "__main__":
    cli()