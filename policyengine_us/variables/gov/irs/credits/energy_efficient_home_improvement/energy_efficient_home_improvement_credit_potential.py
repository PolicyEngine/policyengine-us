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
        p = parameters(period).gov.irs.credits.energy_efficient_home_improvement
        if not p.in_effect:
            return 0

        total = add(tax_unit, period, p.qualified_expenditures.credits)
        # Cap the total (Form 5695 line 28).
        capped_total = min_(total, p.cap.annual.total)
        # 26 U.S.C. 25C(b)(5): after the Inflation Reduction Act, heat pumps
        # etc. have their own cap, notwithstanding the cap on the total, and
        # Form 5695 line 30 adds the two. Before it, they are in the total
        # (pre-IRA is an infinite heat pump etc. cap).
        heat_pump_etc_cap = (
            p.cap.annual.heat_pump_heat_pump_water_heater_biomass_stove_boiler
        )
        if heat_pump_etc_cap == np.inf:
            pre_lifetime_limit = capped_total
        else:
            heat_pump_etc = tax_unit(
                "capped_heat_pump_heat_pump_water_heater_biomass_stove_boiler_credit",
                period,
            )
            pre_lifetime_limit = capped_total + heat_pump_etc
        # Apply lifetime limitation.
        prior_credits = tax_unit(
            "prior_energy_efficient_home_improvement_credits", period
        )
        remaining_credit = p.cap.lifetime.total - prior_credits
        return min_(remaining_credit, pre_lifetime_limit)
