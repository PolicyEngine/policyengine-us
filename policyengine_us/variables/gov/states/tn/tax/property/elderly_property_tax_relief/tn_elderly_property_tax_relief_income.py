from policyengine_us.model_api import *


class tn_elderly_property_tax_relief_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tennessee elderly property tax relief income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TaxReliefBrochure.pdf#page=2",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TCA%2067-5-701%20through%2067-5-704.pdf#page=3",
    )
    defined_for = StateCode.TN

    # AGI is the closest available tax-unit proxy for statutory income from all sources.
    adds = ["adjusted_gross_income"]
