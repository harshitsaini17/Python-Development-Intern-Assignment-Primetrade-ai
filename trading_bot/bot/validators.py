import re
from typing import Optional

from .logging_config import setup_logger

logger = setup_logger("trading_bot.validators")

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP"}
SYMBOL_PATTERN = re.compile(r"^[A-Z]{2,10}USDT$")


class ValidationError(ValueError):
    pass


def validate_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected format like BTCUSDT, ETHUSDT."
        )
    logger.debug(f"Symbol validated: {symbol}")
    return symbol


def validate_side(side: str) -> str:
    side = side.upper().strip()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
        )
    logger.debug(f"Side validated: {side}")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.upper().strip()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    logger.debug(f"Order type validated: {order_type}")
    return order_type


def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be positive, got {qty}.")
    logger.debug(f"Quantity validated: {qty}")
    return qty


def validate_price(price: str) -> float:
    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Price must be positive, got {p}.")
    logger.debug(f"Price validated: {p}")
    return p


def validate_stop_price(stop_price: str) -> float:
    try:
        sp = float(stop_price)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid stop_price '{stop_price}'. Must be a positive number.")
    if sp <= 0:
        raise ValidationError(f"Stop price must be positive, got {sp}.")
    logger.debug(f"Stop price validated: {sp}")
    return sp


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
    time_in_force: Optional[str] = None,
) -> dict:
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)

    validated: dict = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        validated["price"] = validate_price(price)
        validated["timeInForce"] = (time_in_force or "GTC").upper().strip()

    if order_type == "STOP":
        if price is None:
            raise ValidationError("Price (limit price) is required for STOP (stop-limit) orders.")
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP (stop-limit) orders.")
        validated["price"] = validate_price(price)
        validated["stopPrice"] = validate_stop_price(stop_price)
        validated["timeInForce"] = (time_in_force or "GTC").upper().strip()

    logger.info(f"Order params validated successfully: {validated}")
    return validated