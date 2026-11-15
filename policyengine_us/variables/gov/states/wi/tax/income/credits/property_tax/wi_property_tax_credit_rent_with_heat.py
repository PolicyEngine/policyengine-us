from policyengine_us.model_api import *


class wi_property_tax_credit_rent_with_heat(Variable):
    value_type = float
    entity = Person
    label = "Qualified Wisconsin school credit rent with heat (-1 if unknown)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    default_value = -1
    # Each person supplies their own paid, legally attributed qualified amount.
    # Zero is known zero; both heat categories must be known to replace rent.
    reference = (
        "https://docs.legis.wisconsin.gov/2021/statutes/statutes/71.pdf#page=48",
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-inst.pdf#page=18",
    )
