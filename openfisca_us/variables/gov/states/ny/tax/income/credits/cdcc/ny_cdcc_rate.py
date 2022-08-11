from openfisca_us.model_api import *


class ny_cdcc_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CDCC rate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        ny_agi = tax_unit("ny_agi", period)
        federal_rate = tax_unit("cdcc_rate", period)

        ny_cdcc = parameters(period).gov.states.ny.tax.income.credits.cdcc
        first_threshold = ny_cdcc.multiplier.phase_out.first.start
        second_threshold = ny_cdcc.multiplier.phase_out.first.end
        below_main_phase_out = ny_agi <= first_threshold
        in_main_phase_out = ny_agi > first_threshold
        in_second_phase_out = ny_agi > second_threshold
        percent_along_first_phase_out = (ny_agi - first_threshold) / (
            second_threshold - first_threshold
        )
        multiplier_max = ny_cdcc.multiplier.max
        # Interpolate between the max and 1
        interpolated_first_phase_out_rate = multiplier_max + (
            percent_along_first_phase_out * (1 - multiplier_max)
        )
        second_phase_out_rate = ny_cdcc.multiplier.phase_out.second.rate
        multiplier_floor = ny_cdcc.multiplier.addition
        additional_multiplier = ny_cdcc.multiplier.additional_multiplier.calc(ny_agi)

        ny_multiplier = additional_multiplier * select(
            [
                below_main_phase_out,
                in_main_phase_out,
                in_second_phase_out,
            ],
            [
                multiplier_max,
                interpolated_first_phase_out_rate,
                min_(
                    multiplier_floor,
                    1 - second_phase_out_rate * ny_agi / 1_000,
                ),
            ],
        )

        return federal_rate * ny_multiplier
