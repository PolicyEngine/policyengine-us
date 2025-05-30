from policyengine_us.model_api import *


class energy_efficient_home_improvement_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Potential value of the Energy efficient home improvement credit"
    documentation = "Residential clean energy credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        if not p.in_effect:
            return 0

        heat_pump_etc = tax_unit(
            "capped_heat_pump_heat_pump_water_heater_biomass_stove_boiler_credit",
            period,
        )
        total = add(tax_unit, period, p.qualified_expenditures.credits)
        # Cap the total.
        capped_total = min_(total, p.cap.annual.total)
        # Before the lifetime limit, it can either be the total or the heat pump/etc.
        pre_lifetime_limit = max_(capped_total, heat_pump_etc)
        # Apply lifetime limitation.
        prior_credits = tax_unit(
            "prior_energy_efficient_home_improvement_credits", period
        )
        remaining_credit = p.cap.lifetime.total - prior_credits
        return min_(remaining_credit, pre_lifetime_limit)
