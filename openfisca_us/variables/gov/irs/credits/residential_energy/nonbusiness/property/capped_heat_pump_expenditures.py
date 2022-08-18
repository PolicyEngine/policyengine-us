from openfisca_us.model_api import *


class capped_heat_pump_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped electric or natural gas heat pump expenditures"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=340"

    def formula(tax_unit, period, parameters):
        uncapped = tax_unit("heat_pump_expenditures", period)
        p = parameters(period).gov.irs.credits.residential_energy.nonbusiness
        return min_(uncapped, p.cap.annual.heat_pumps_stoves_boilers)
