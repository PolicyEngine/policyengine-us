from policyengine_us.model_api import *


class hi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        regular_exemptions = tax_unit("hi_regular_exemptions", period)
        disabled_exemptions = tax_unit("hi_disabled_exemptions", period)
        return max_(regular_exemptions, disabled_exemptions)
