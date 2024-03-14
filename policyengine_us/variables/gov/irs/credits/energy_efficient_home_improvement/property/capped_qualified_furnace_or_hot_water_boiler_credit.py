from policyengine_us.model_api import *


class capped_qualified_furnace_or_hot_water_boiler_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Capped qualified furnace or hot water boiler credit"
    documentation = "Capped qualified furnace or hot water boiler credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_3_B"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        expenditure = tax_unit(
            "qualified_furnace_or_hot_water_boiler_expenditures", period
        )
        rate = p.rates.property
        uncapped = expenditure * rate
        # Cap at either the furnace/boiler cap (pre-IRA) or total property cap (post-IRA).
        cap = min_(
            p.cap.annual.qualified_furnace_or_hot_water_boiler,
            p.cap.annual.energy_efficient_building_property,
        )
        return min_(uncapped, cap)
