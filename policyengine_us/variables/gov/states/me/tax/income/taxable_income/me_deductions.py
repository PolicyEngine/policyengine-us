from policyengine_us.model_api import *


class me_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine income deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5124-C.html",
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_item_stand_%20ded_phaseout_wksht.pdf",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # Get the phaseout percent (Line 5).
        phaseout_percent = tax_unit("me_deduction_phaseout_percentage", period)

        # Get the relevant deduction amount (Line 6).
        # Either itemized deduction or federal standard deduction.
        itemizes = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("standard_deduction", period)
        larger_deduction = max_(
            tax_unit("me_itemized_deductions_pre_phaseout", period),
            standard_deduction,
        )
        max_deduction = where(itemizes, larger_deduction, standard_deduction)

        # Calculate the phaseout amount (Line 7).
        phaseout_amount = max_deduction * phaseout_percent

        # Calculate the deduction after phaseout (Line 8).
        # Note this cannot be negative because phaseout_percent is capped at 1.
        return max_deduction - phaseout_amount
