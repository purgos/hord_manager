"""
Currency and value conversion service for Hord Manager.

This service handles all conversions between different currencies and units,
using ounces of gold as the base unit for all value calculations.
"""

from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from decimal import Decimal, ROUND_HALF_UP

from ..models.currency import Currency, CurrencyDenomination
from ..models.metal import MetalPriceHistory
from ..models.gemstone import Gemstone
from ..core.database import get_db


class ConversionService:
    """Service for handling currency and value conversions."""
    
    # Standard conversion constants
    OUNCES_PER_POUND = 16.0
    CARATS_PER_OUNCE = 141.75  # 1 oz = 141.75 carats (troy ounce conversion)
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_gold_price_usd(self, session_number: Optional[int] = None) -> float:
        """Get current USD price per ounce of gold."""
        query = self.db.query(MetalPriceHistory).filter(
            MetalPriceHistory.metal_name == "Gold",
            MetalPriceHistory.unit == "oz"
        )
        
        if session_number:
            query = query.filter(MetalPriceHistory.session_number == session_number)
        
        gold_price = query.order_by(MetalPriceHistory.created_at.desc()).first()
        
        if not gold_price:
            # Fallback to a reasonable default if no gold price available
            return 2000.0  # $2000/oz as fallback
        
        return gold_price.price_per_unit_usd
    
    def oz_gold_to_usd(self, oz_gold: float, session_number: Optional[int] = None) -> float:
        """Convert ounces of gold to USD."""
        gold_price = self.get_gold_price_usd(session_number)
        return oz_gold * gold_price
    
    def usd_to_oz_gold(self, usd_amount: float, session_number: Optional[int] = None) -> float:
        """Convert USD to ounces of gold."""
        gold_price = self.get_gold_price_usd(session_number)
        return usd_amount / gold_price
    
    def oz_gold_to_currency(self, oz_gold: float, currency_name: str) -> float:
        """Convert ounces of gold to specified currency base units."""
        currency = self.db.query(Currency).filter(Currency.name == currency_name).first()
        
        if not currency:
            raise ValueError(f"Currency '{currency_name}' not found")
        
        if currency.base_unit_value_oz_gold == 0:
            raise ValueError(f"Currency '{currency_name}' has no conversion rate set")
        
        return oz_gold / currency.base_unit_value_oz_gold
    
    def currency_to_oz_gold(self, amount: float, currency_name: str) -> float:
        """Convert currency base units to ounces of gold."""
        currency = self.db.query(Currency).filter(Currency.name == currency_name).first()
        
        if not currency:
            raise ValueError(f"Currency '{currency_name}' not found")
        
        return amount * currency.base_unit_value_oz_gold
    
    def convert_between_currencies(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert between two currencies via gold."""
        # Convert to gold first, then to target currency
        oz_gold = self.currency_to_oz_gold(amount, from_currency)
        return self.oz_gold_to_currency(oz_gold, to_currency)
    
    def metal_value_to_oz_gold(self, metal_name: str, amount: float, unit: str, 
                              session_number: Optional[int] = None) -> float:
        """Convert metal amount to ounces of gold equivalent."""
        # Get latest price for the metal
        query = self.db.query(MetalPriceHistory).filter(
            MetalPriceHistory.metal_name == metal_name
        )
        
        if session_number:
            query = query.filter(MetalPriceHistory.session_number == session_number)
        
        metal_price = query.order_by(MetalPriceHistory.created_at.desc()).first()
        
        if not metal_price:
            raise ValueError(f"No price data found for metal '{metal_name}'")
        
        # Convert units if necessary
        if unit == "lb" and metal_price.unit == "oz":
            # Convert pounds to ounces
            amount_in_price_unit = amount * self.OUNCES_PER_POUND
        elif unit == "oz" and metal_price.unit == "lb":
            # Convert ounces to pounds
            amount_in_price_unit = amount / self.OUNCES_PER_POUND
        elif unit == metal_price.unit:
            amount_in_price_unit = amount
        else:
            raise ValueError(f"Cannot convert {unit} to {metal_price.unit} for {metal_name}")
        
        # Calculate value in gold ounces
        return amount_in_price_unit * metal_price.price_per_oz_gold
    
    def gemstone_value_to_oz_gold(self, gemstone_name: str, carats: float) -> float:
        """Convert gemstone carats to ounces of gold equivalent."""
        gemstone = self.db.query(Gemstone).filter(Gemstone.name == gemstone_name).first()
        
        if not gemstone:
            raise ValueError(f"Gemstone '{gemstone_name}' not found")
        
        if gemstone.value_per_carat_oz_gold == 0:
            raise ValueError(f"Gemstone '{gemstone_name}' has no value set")
        
        return carats * gemstone.value_per_carat_oz_gold
    
    def format_currency_with_denominations(self, amount: float, currency_name: str) -> Dict:
        """Format currency amount with appropriate denominations."""
        currency = self.db.query(Currency).filter(Currency.name == currency_name).first()
        
        if not currency:
            raise ValueError(f"Currency '{currency_name}' not found")
        
        # Get denominations sorted by value (largest first)
        denominations = sorted(currency.denominations, 
                             key=lambda d: d.value_in_base_units, reverse=True)
        
        if not denominations:
            return {
                "currency": currency_name,
                "total": amount,
                "breakdown": [],
                "formatted": f"{amount:.2f} {currency_name}"
            }
        
        breakdown = []
        remaining = Decimal(str(amount))
        
        for denom in denominations:
            denom_value = Decimal(str(denom.value_in_base_units))
            if remaining >= denom_value:
                count = int(remaining / denom_value)
                remaining = remaining % denom_value
                breakdown.append({
                    "denomination": denom.name,
                    "count": count,
                    "value": float(denom_value),
                    "total_value": float(count * denom_value)
                })
        
        # Add any remaining fractional amount
        if remaining > 0:
            breakdown.append({
                "denomination": f"fractional {currency_name}",
                "count": 1,
                "value": float(remaining),
                "total_value": float(remaining)
            })
        
        # Create formatted string
        if breakdown:
            parts = []
            for item in breakdown:
                if item["denomination"].startswith("fractional"):
                    parts.append(f"{item['value']:.4f}")
                else:
                    parts.append(f"{item['count']} {item['denomination']}")
            formatted = " + ".join(parts)
        else:
            formatted = f"{amount:.2f} {currency_name}"
        
        return {
            "currency": currency_name,
            "total": amount,
            "breakdown": breakdown,
            "formatted": formatted
        }
    
    def get_conversion_rates(self, base_currency: str = "USD") -> Dict:
        """Get conversion rates for all currencies relative to base currency."""
        currencies = self.db.query(Currency).all()
        rates = {}
        
        try:
            # Get base currency value in gold
            if base_currency == "USD":
                base_oz_gold_rate = 1 / self.get_gold_price_usd()
            else:
                base_currency_obj = next((c for c in currencies if c.name == base_currency), None)
                if not base_currency_obj:
                    raise ValueError(f"Base currency '{base_currency}' not found")
                base_oz_gold_rate = base_currency_obj.base_unit_value_oz_gold
            
            for currency in currencies:
                if currency.base_unit_value_oz_gold > 0:
                    # Rate = how many units of this currency = 1 unit of base currency
                    rates[currency.name] = base_oz_gold_rate / currency.base_unit_value_oz_gold
                else:
                    rates[currency.name] = 0.0
            
            # Add USD if not already included
            if base_currency != "USD":
                usd_in_gold = 1 / self.get_gold_price_usd()
                rates["USD"] = base_oz_gold_rate / usd_in_gold
            
        except Exception as e:
            # Return empty rates on error
            rates = {currency.name: 0.0 for currency in currencies}
        
        return {
            "base_currency": base_currency,
            "rates": rates,
            "last_updated": "current_session"  # Could be enhanced with timestamps
        }
    
    def convert_value_display(self, oz_gold_value: float, target_currencies: Optional[List[str]] = None) -> Dict:
        """Convert a gold value to multiple currency displays."""
        if target_currencies is None:
            # Default to USD and all configured currencies
            currencies = self.db.query(Currency).all()
            target_currencies = ["USD"] + [c.name for c in currencies]
        
        conversions = {}
        
        for currency_name in target_currencies:
            try:
                if currency_name == "USD":
                    amount = self.oz_gold_to_usd(oz_gold_value)
                    conversions[currency_name] = {
                        "amount": amount,
                        "formatted": f"${amount:,.2f}",
                        "breakdown": None
                    }
                else:
                    amount = self.oz_gold_to_currency(oz_gold_value, currency_name)
                    breakdown = self.format_currency_with_denominations(amount, currency_name)
                    conversions[currency_name] = {
                        "amount": amount,
                        "formatted": breakdown["formatted"],
                        "breakdown": breakdown["breakdown"]
                    }
            except (ValueError, Exception):
                # Skip currencies that can't be converted
                continue
        
        return {
            "oz_gold_value": oz_gold_value,
            "conversions": conversions
        }


def get_conversion_service(db: Session) -> ConversionService:
    """Factory function to get conversion service instance."""
    return ConversionService(db)