from policyengine_us.model_api import *


class nj_property_tax_relief(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax relief benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/treasury/taxation/relief.shtml",
        "https://www.nj.gov/treasury/taxation/staynj/calculation.shtml",
    )
    defined_for = StateCode.NJ

    def formula_2026(tax_unit, period, parameters):
        return (
            tax_unit("nj_anchor", period)
            + tax_unit("nj_capped_senior_freeze", period)
            + tax_unit("nj_staynj", period)
        )
