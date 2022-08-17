from openfisca_us.model_api import *


class capped_energy_efficient_building_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped energy-efficient building property expenditures"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_3_C"

    def formula(tax_unit, period, parameters):
        uncapped = tax_unit(
            "energy_efficient_building_property_expenditures", period
        )
        p = parameters(period).gov.irs.credits.residential_energy.nonbusiness
        return min_(uncapped, p.cap.energy_efficient_building_property)
