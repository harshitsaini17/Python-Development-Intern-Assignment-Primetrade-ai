from datetime import datetime
from typing import Optional

from .client import BinanceFuturesClient, BinanceAPIError, BinanceConnectionError
from .validators import validate_order_params, ValidationError
from .logging_config import setup_logger

logger = setup_logger("trading_bot.orders")


class OrderManager:
    def __init__(self, client: BinanceFuturesClient):
        self.client = client

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        stop_price: Optional[str] = None,
        time_in_force: Optional[str] = None,
    ) -> dict:
        try:
            validated = validate_order_params(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                time_in_force=time_in_force,
            )
        except ValidationError as e:
            logger.error(f"Validation failed: {e}")
            raise

        params = {
            "symbol": validated["symbol"],
            "side": validated["side"],
            "type": validated["type"],
            "quantity": validated["quantity"],
        }

        if "price" in validated:
            params["price"] = validated["price"]

        if "stopPrice" in validated:
            params["stopPrice"] = validated["stopPrice"]

        if "timeInForce" in validated:
            params["timeInForce"] = validated["timeInForce"]

        logger.info(f"Sending order to Binance: {params}")

        try:
            if validated["type"] == "STOP":
                response = self.client.place_stop_order(**params)
            else:
                response = self.client.place_order(**params)
        except BinanceAPIError as e:
            logger.error(f"Binance API error: {e}")
            raise
        except BinanceConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise

        logger.info(f"Order response: {response}")
        return response


def format_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> str:
    lines = [
        "=" * 50,
        "   ORDER REQUEST SUMMARY",
        "=" * 50,
        f"  Symbol     : {symbol}",
        f"  Side       : {side}",
        f"  Type       : {order_type}",
        f"  Quantity   : {quantity}",
    ]
    if price:
        lines.append(f"  Price      : {price}")
    if stop_price:
        lines.append(f"  Stop Price : {stop_price}")
    lines.append("=" * 50)
    return "\n".join(lines)


def format_order_response(response: dict) -> str:
    fields = {
        "orderId": "Order ID",
        "algoOrderId": "Algo Order ID",
        "symbol": "Symbol",
        "status": "Status",
        "side": "Side",
        "type": "Type",
        "quantity": "Original Qty",
        "origQty": "Original Qty",
        "price": "Price",
        "stopPrice": "Stop Price",
        "executedQty": "Executed Qty",
        "avgPrice": "Avg Price",
        "timeInForce": "Time in Force",
        "updateTime": "Update Time",
        "clientOrderId": "Client Order ID",
    }

    lines = [
        "=" * 50,
        "   ORDER RESPONSE",
        "=" * 50,
    ]

    for key, label in fields.items():
        value = response.get(key, "N/A")
        if key == "updateTime" and value != "N/A":
            try:
                value = datetime.fromtimestamp(int(value) / 1000).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except (ValueError, TypeError, OSError):
                pass
        if value != "N/A":
            lines.append(f"  {label:16s}: {value}")

    lines.append("=" * 50)
    return "\n".join(lines)