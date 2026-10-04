from decimal import Decimal, ROUND_HALF_UP
from typing import List
from app.models.formula import Formula
from app.schemas.calculation import CalculationResponse, CalculatedComponent


class CalculationService:
    @staticmethod
    def calculate(formula: Formula, target_amount: Decimal, unit: str = "g") -> CalculationResponse:
        """
        Calculates proportional amounts of each component in a formula
        based on a requested target_amount.
        Uses exact Decimal arithmetic.
        """
        if target_amount <= Decimal("0"):
            raise ValueError("Target amount must be strictly greater than zero.")

        base_total = Decimal(str(formula.base_total_amount))
        if base_total <= Decimal("0"):
            raise ValueError("Formula base total amount must be strictly greater than zero.")

        # Scaling factor: target_amount / base_total
        factor = (target_amount / base_total)

        calculated_components: List[CalculatedComponent] = []
        running_cumulative = Decimal("0.0000")

        # Sort components by sort_order
        sorted_components = sorted(formula.components, key=lambda c: (c.sort_order, c.id))

        for comp in sorted_components:
            orig_amount = Decimal(str(comp.amount))
            # Calculate scaled amount with 4 decimal places precision (or 2 for display)
            scaled_amount = (orig_amount * factor).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            running_cumulative += scaled_amount

            # Percentage of original formula
            pct = ((orig_amount / base_total) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            calculated_components.append(
                CalculatedComponent(
                    component_code=comp.component_code,
                    component_name=comp.component_name,
                    amount=scaled_amount,
                    cumulative_amount=running_cumulative.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
                    percentage=pct,
                    unit=unit,
                    sort_order=comp.sort_order,
                    notes=comp.notes,
                )
            )

        total_calculated = sum(c.amount for c in calculated_components)

        # Brand and model names if available
        brand_name = formula.color.brand.name if formula.color and formula.color.brand else None
        model_name = formula.color.model.name if formula.color and formula.color.model else None
        color_code = formula.color.color_code if formula.color else ""
        color_name = formula.color.color_name if formula.color else ""

        return CalculationResponse(
            formula_id=formula.id,
            formula_name=formula.formula_name,
            variant_name=formula.variant_name,
            version=formula.version,
            color_code=color_code,
            color_name=color_name,
            brand_name=brand_name,
            model_name=model_name,
            target_amount=target_amount,
            base_total_amount=base_total,
            unit=unit,
            factor=factor.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP),
            components=calculated_components,
            total=total_calculated,
        )
