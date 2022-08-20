from openfisca_us.model_api import *


class capped_heat_pump_heat_pump_water_heater_biomass_stove_boiler_expenditures(
    Variable
):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped expenditures on heat pumps, heat pump water heaters, and biomass stoves and boilers"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=340"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        uncapped = add(
            tax_unit,
            p.qualifying_expenditures.heat_pump_heat_pump_water_heater_biomass_stove_boiler,
            period,
        )
        return min_(
            uncapped,
            p.cap.annual.heat_pump_heat_pump_water_heater_biomass_stove_boiler,
        )


"""
HEAT PUMP AND HEAT PUMP WATER HEAT2 ERS; BIOMASS STOVES AND BOILERS.—Notwith3 standing paragraphs (1) and (2), the credit allowed
4 under this section by reason of subsection (a)(2) with
5 respect to any taxpayer for any taxable year shall
6 not, in the aggregate, exceed $2,000 with respect to
7 amounts paid or incurred for property described in
8 clauses (i) and (ii) of subsection (d)(2)(A) and in
9 subsection (d)(2)(B)

(d)(2)(A)
(i) An electric or natural gas heat
16 pump water heater.
17 ‘‘(ii) An electric or natural gas heat
18 pump. 

(d)(2)(B)
A biomass stove or boiler which—
"""
