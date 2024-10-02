from policyengine_us.model_api import *


class capped_advanced_main_air_circulating_fan_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Capped advanced main air circulating fan credit"
    documentation = "Capped advanced main air circulating fan credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_3_A"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        expenditure = tax_unit(
            "advanced_main_air_circulating_fan_expenditures", period
        )
        rate = p.rates.property
        uncapped = expenditure * rate
        # Cap at either the fan cap (pre-IRA) or total property cap (post-IRA).
        cap = min_(
            p.cap.annual.advanced_main_air_circulating_fan,
            p.cap.annual.energy_efficient_building_property,
        )
        return min_(uncapped, cap)
