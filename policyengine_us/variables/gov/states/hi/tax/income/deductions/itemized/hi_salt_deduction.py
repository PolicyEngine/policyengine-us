from policyengine_us.model_api import *


class hi_salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii state and local tax deduction"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=18"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32"  # total itemized deduction worksheet
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    # Hawaii's state income tax allows an itemized deduction for state income taxes paid.
    # Hawaii does not cap the SALT deduction as the US does.

    adds = ["state_and_local_sales_or_income_tax", "real_estate_taxes"]
