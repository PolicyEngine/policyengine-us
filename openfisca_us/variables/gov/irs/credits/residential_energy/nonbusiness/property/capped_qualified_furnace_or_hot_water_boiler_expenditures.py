from openfisca_us.model_api import *


class capped_qualified_furnace_or_hot_water_boiler_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped qualified furnace or hot water boiler expenditures"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_3_B"

    def formula(tax_unit, period, parameters):
        uncapped = tax_unit(
            "qualified_furnace_or_hot_water_boiler_expenditures", period
        )
        p = parameters(period).gov.irs.credits.residential_energy.nonbusiness
        return min_(uncapped, p.cap.qualified_furnace_or_hot_water_boiler)
