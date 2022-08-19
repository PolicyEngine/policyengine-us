from openfisca_us.model_api import *


class capped_energy_efficient_door_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped energy-efficient exterior door expenditures"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339"

    def formula(tax_unit, period, parameters):
        uncapped = tax_unit("energy_efficient_door_expenditures", period)
        p = parameters(period).gov.irs.credits.residential_energy.nonbusiness
        return min_(uncapped, p.cap.annual.door)
