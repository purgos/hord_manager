"""
Currency and value conversion service for Hord Manager.

This service handles all conversions between different currencies and units,
using USD as the base unit for all value calculations with flexible pegging.
"""

from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from decimal import Decimal, ROUND_HALF_UP

from ..models.currency import Currency, CurrencyDenomination, PegType
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
    
    def currency_to_usd(self, amount: float, currency_name: str, session_number: Optional[int] = None) -> float:
        """Convert currency to USD using the flexible pegging system."""
        if currency_name == "USD":
            return amount
            
        currency = self.db.query(Currency).filter(Currency.name == currency_name).first()
        
        if not currency:
            raise ValueError(f"Currency '{currency_name}' not found")
        
        if currency.base_unit_value == 0:
            raise ValueError(f"Currency '{currency_name}' has no conversion rate set")
        
        if currency.peg_type == PegType.CURRENCY:
            if currency.peg_target == "USD":
                return amount * currency.base_unit_value
            else:
                # Convert through the peg target currency
                target_usd = self.currency_to_usd(currency.base_unit_value, currency.peg_target, session_number)
                return amount * target_usd
        elif currency.peg_type == PegType.METAL:
            # Convert through metal pricing (e.g., gold)
            if currency.peg_target.lower() == "gold":
                gold_price_usd = self.get_gold_price_usd(session_number)
                oz_gold_value = amount * currency.base_unit_value
                return oz_gold_value * gold_price_usd
            else:
                raise ValueError(f"Metal peg to '{currency.peg_target}' not yet supported")
        elif currency.peg_type == PegType.MATERIAL:
            raise ValueError(f"Material pegging not yet supported")
        else:
            raise ValueError(f"Unknown peg type: {currency.peg_type}")
    
    def usd_to_currency(self, usd_amount: float, currency_name: str, session_number: Optional[int] = None) -> float:
        """Convert USD to specified currency using the flexible pegging system."""
        if currency_name == "USD":
            return usd_amount
            
        currency = self.db.query(Currency).filter(Currency.name == currency_name).first()
        
        if not currency:
            raise ValueError(f"Currency '{currency_name}' not found")
        
        if currency.base_unit_value == 0:
            raise ValueError(f"Currency '{currency_name}' has no conversion rate set")
        
        if currency.peg_type == PegType.CURRENCY:
            if currency.peg_target == "USD":
                return usd_amount / currency.base_unit_value
            else:
                # Convert through the peg target currency
                target_amount = self.usd_to_currency(usd_amount, currency.peg_target, session_number)
                return target_amount / currency.base_unit_value
        elif currency.peg_type == PegType.METAL:
            # Convert through metal pricing (e.g., gold)
            if currency.peg_target.lower() == "gold":
                gold_price_usd = self.get_gold_price_usd(session_number)
                oz_gold_value = usd_amount / gold_price_usd
                return oz_gold_value / currency.base_unit_value
            else:
                raise ValueError(f"Metal peg to '{currency.peg_target}' not yet supported")
        elif currency.peg_type == PegType.MATERIAL:
            raise ValueError(f"Material pegging not yet supported")
        else:
            raise ValueError(f"Unknown peg type: {currency.peg_type}")
    
    def oz_gold_to_currency(self, oz_gold: float, currency_name: str, session_number: Optional[int] = None) -> float:
        """Convert ounces of gold to specified currency base units."""
        # Convert gold to USD first, then to target currency
        usd_amount = self.oz_gold_to_usd(oz_gold, session_number)
        return self.usd_to_currency(usd_amount, currency_name, session_number)
    
    def currency_to_oz_gold(self, amount: float, currency_name: str, session_number: Optional[int] = None) -> float:
        """Convert currency base units to ounces of gold."""
        # Convert currency to USD first, then to gold
        usd_amount = self.currency_to_usd(amount, currency_name, session_number)
        return self.usd_to_oz_gold(usd_amount, session_number)
    
    def convert_between_currencies(self, amount: float, from_currency: str, to_currency: str, session_number: Optional[int] = None) -> float:
        """Convert between two currencies via USD."""
        # Convert to USD first, then to target currency
        usd_amount = self.currency_to_usd(amount, from_currency, session_number)
        return self.usd_to_currency(usd_amount, to_currency, session_number)
    
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
    
    def get_conversion_rates(self, base_currency: str = "USD", session_number: Optional[int] = None) -> Dict:
        """Get conversion rates for all currencies relative to base currency."""
        currencies = self.db.query(Currency).all()
        rates = {}
        
        try:
            for currency in currencies:
                if currency.base_unit_value > 0:
                    try:
                        # Rate = how many units of this currency = 1 unit of base currency
                        if base_currency == "USD":
                            rates[currency.name] = 1.0 / self.currency_to_usd(1.0, currency.name, session_number)
                        else:
                            # Convert 1 unit of base currency to USD, then to target currency
                            base_usd = self.currency_to_usd(1.0, base_currency, session_number)
                            rates[currency.name] = self.usd_to_currency(base_usd, currency.name, session_number)
                    except (ValueError, Exception):
                        rates[currency.name] = 0.0
                else:
                    rates[currency.name] = 0.0
            
            # Add USD if not already included
            if "USD" not in rates:
                if base_currency == "USD":
                    rates["USD"] = 1.0
                else:
                    try:
                        base_usd = self.currency_to_usd(1.0, base_currency, session_number)
                        rates["USD"] = 1.0 / base_usd
                    except (ValueError, Exception):
                        rates["USD"] = 0.0
            
        except Exception as e:
            # Return empty rates on error
            rates = {currency.name: 0.0 for currency in currencies}
            rates["USD"] = 1.0 if base_currency == "USD" else 0.0
        
        return {
            "base_currency": base_currency,
            "rates": rates,
            "last_updated": "current_session"  # Could be enhanced with timestamps
        }
    
    def convert_value_display(self, usd_value: float, target_currencies: Optional[List[str]] = None, session_number: Optional[int] = None) -> Dict:
        """Convert a USD value to multiple currency displays."""
        if target_currencies is None:
            # Default to USD and all configured currencies
            currencies = self.db.query(Currency).all()
            target_currencies = ["USD"] + [c.name for c in currencies]
        
        conversions = {}
        
        for currency_name in target_currencies:
            try:
                if currency_name == "USD":
                    conversions[currency_name] = {
                        "amount": usd_value,
                        "formatted": f"${usd_value:,.2f}",
                        "breakdown": None
                    }
                else:
                    amount = self.usd_to_currency(usd_value, currency_name, session_number)
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
            "usd_value": usd_value,
            "conversions": conversions
        }
    
    def convert_gold_value_display(self, oz_gold_value: float, target_currencies: Optional[List[str]] = None, session_number: Optional[int] = None) -> Dict:
        """Convert a gold value to multiple currency displays (legacy method for backward compatibility)."""
        usd_value = self.oz_gold_to_usd(oz_gold_value, session_number)
        result = self.convert_value_display(usd_value, target_currencies, session_number)
        result["oz_gold_value"] = oz_gold_value  # Add gold value for compatibility
        return result


def get_conversion_service(db: Session) -> ConversionService:
    """Factory function to get conversion service instance."""
    return ConversionService(db)