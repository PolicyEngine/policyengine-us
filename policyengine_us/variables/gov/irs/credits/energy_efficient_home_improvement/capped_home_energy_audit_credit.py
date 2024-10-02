from policyengine_us.model_api import *


class capped_home_energy_audit_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped home energy audit credit"
    definition_period = YEAR
    documentation = "Capped home energy audit credit"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=366"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        expenditure = tax_unit("home_energy_audit_expenditures", period)
        rate = p.rates.home_energy_audit
        uncapped = expenditure * rate
        # Cap at either the fan cap (pre-IRA) or total property cap (post-IRA).
        cap = p.cap.annual.home_energy_audit
        return min_(uncapped, cap)
