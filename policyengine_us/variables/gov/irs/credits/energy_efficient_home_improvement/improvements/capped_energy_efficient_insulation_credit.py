from policyengine_us.model_api import *


class capped_energy_efficient_insulation_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped credit on energy-efficient insulation material"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339"

    def formula(tax_unit, period, parameters):
        pre_rebate_expenditure = tax_unit(
            "energy_efficient_insulation_expenditures", period
        )
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        # NB: We assume that the credit is based on after-rebate expenditures,
        # where rebates are per-item before the total rebate cap is applied.
        # We also assume all rebates for insulation, air sealing, and ventilation
        # are for insulation. Otherwise would require allocating the rebate
        # across subcategories.
        rebate = tax_unit(
            "capped_insulation_air_sealing_ventilation_rebate", period
        )
        # Cap at zero in case they have a rebate from air sealing and ventilation
        # but no insulation expenditures.
        post_rebate_expenditure = max_(0, pre_rebate_expenditure - rebate)
        rate = p.rates.improvements
        uncapped = post_rebate_expenditure * rate
        return min_(uncapped, p.cap.annual.insulation_material)
