from openfisca_us.model_api import *


class capped_central_air_conditioner_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped central air conditioner expenditures"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_3_A"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        expenditure = tax_unit("central_air_conditioner_expenditures", period)
        rate = p.rates.property
        uncapped = expenditure * rate
        # Cap at either the conditioner cap (pre-IRA) or total property cap (post-IRA).
        cap = min_(
            p.cap.annual.central_air_conditioner,
            p.cap.annual.energy_efficient_building_property,
        )
        return min_(uncapped, cap)
