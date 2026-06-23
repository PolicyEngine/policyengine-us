from policyengine_us.model_api import *


class nj_capped_senior_freeze(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey capped Senior Freeze benefit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/treasury/taxation/staynj/calculation.shtml",
        "https://www.nj.gov/treasury/taxation/ptr/index.shtml",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        anchor = tax_unit("nj_anchor", period)
        senior_freeze = tax_unit("nj_senior_freeze", period)
        return min_(senior_freeze, max_(property_taxes - anchor, 0))
