from policyengine_us.model_api import *


class dwks13(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 4 of 6)"
    unit = USD

    def formula(tax_unit, period, parameters):
        e24515 = add(tax_unit, period, ["unrecaptured_section_1250_gain"])
        dwks11 = e24515 + add(
            tax_unit, period, ["capital_gains_28_percent_rate_gain"]
        )  # Sch D lines 18 and 19, respectively
        dwks09 = tax_unit("dwks09", period)
        dwks12 = min_(dwks09, dwks11)
        dwks10 = tax_unit("dwks10", period)
        return (dwks10 - dwks12) * tax_unit("has_qdiv_or_ltcg", period)
