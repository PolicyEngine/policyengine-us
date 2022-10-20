from policyengine_us.model_api import *


class capped_insulation_air_sealing_ventilation_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped insulation air sealing and ventilation rebate"
    documentation = "Before total high efficiency electric home rebate cap"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        percent_covered = tax_unit(
            "high_efficiency_electric_home_rebate_percent_covered", period
        )
        expenditures = add(
            tax_unit,
            period,
            # NB: Separated because insulation also receives a tax credit.
            [
                "energy_efficient_insulation_expenditures",
                "air_sealing_ventilation_expenditures",
            ],
        )
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.insulation_air_sealing_ventilation
        return min_(expenditures * percent_covered, cap)
