from policyengine_us.model_api import *


class or_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html"  # 316.695 (1)(d)
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        federal_deductions_if_itemizing = parameters(
            period
        ).gov.irs.deductions.deductions_if_itemizing
        or_deductions_if_itemizing = [
            deduction
            for deduction in federal_deductions_if_itemizing
            if deduction
            not in [
                "salt_deduction",
                # Exclude QBID to avoid circular reference.
                "qualified_business_income_deduction",
            ]
        ]
        return add(tax_unit, period, or_deductions_if_itemizing)
