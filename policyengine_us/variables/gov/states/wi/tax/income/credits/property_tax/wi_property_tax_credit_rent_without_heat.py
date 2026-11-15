from policyengine_us.model_api import *


class wi_property_tax_credit_rent_without_heat(Variable):
    value_type = float
    entity = Person
    label = "Qualified Wisconsin school credit rent without heat (-1 if unknown)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    default_value = -1
    # Exclude services, business expenses and unqualified tax-exempt housing.
    # Supply zero explicitly when none of this person's qualified rent excludes heat.
    reference = (
        "https://docs.legis.wisconsin.gov/2021/statutes/statutes/71.pdf#page=48",
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-inst.pdf#page=18",
    )
