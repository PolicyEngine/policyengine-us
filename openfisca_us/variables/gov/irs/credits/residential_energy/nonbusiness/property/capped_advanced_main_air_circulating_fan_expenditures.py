from openfisca_us.model_api import *


class capped_advanced_main_air_circulating_fan_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped advanced main air circulating fan expenditures"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_3_A"

    def formula(tax_unit, period, parameters):
        uncapped = tax_unit(
            "advanced_main_air_circulating_fan_expenditures", period
        )
        p = parameters(period).gov.irs.credits.residential_energy.nonbusiness
        return min_(uncapped, p.cap.advanced_main_air_circulating_fan)
