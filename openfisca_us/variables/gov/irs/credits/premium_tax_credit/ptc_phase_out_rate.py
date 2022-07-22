from openfisca_us.model_api import *


class ptc_phase_out_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "PTC phase-out rate"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B#b_3_A"

    def formula(tax_unit, period, parameters):
        ptc = parameters(period).gov.irs.credits.premium_tax_credit
        income_level = tax_unit.value_from_first_person(
            tax_unit.members("medicaid_income_level", period)
        )
        rates = income_level * 0
        lower = ptc.phase_out.starting_rate
        upper = ptc.phase_out.ending_rate
        for i in range(len(lower.thresholds)):
            lower_threshold = lower.thresholds[i]
            upper_threshold = (
                lower.thresholds[i + 1]
                if i + 1 < len(lower.thresholds)
                else inf
            )
            in_bracket = (income_level >= lower_threshold) & (
                income_level < upper_threshold
            )
            percent_through_bracket = (income_level - lower_threshold) / (
                upper_threshold - lower_threshold
            )
            rate_in_bracket = (
                upper.amounts[i] - lower.amounts[i]
            ) * percent_through_bracket + lower.amounts[i]
            rates[in_bracket] = rate_in_bracket[in_bracket]
        return rates
