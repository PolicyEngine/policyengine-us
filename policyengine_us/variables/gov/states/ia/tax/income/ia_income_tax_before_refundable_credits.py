from policyengine_us.model_api import *


class ia_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=60"
        "https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=60"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        tax_before = tax_unit("ia_income_tax_before_credits", period)
        nonref_credits = tax_unit("ia_nonrefundable_credits", period)
        is_tax_exempt = tax_unit("ia_is_tax_exempt", period)
        tax_after = ~is_tax_exempt * max_(0, tax_before - nonref_credits)
        tax_reduced = tax_unit("ia_reduced_tax", period)
        return min_(tax_after, tax_reduced)
