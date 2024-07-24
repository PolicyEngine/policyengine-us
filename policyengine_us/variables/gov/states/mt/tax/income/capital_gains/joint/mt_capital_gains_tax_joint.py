from policyengine_us.model_api import *


class mt_capital_gains_tax_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana net long-term capital gains tax when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/12/Form_2_2023_Instructions.pdf#page=6"  # Net Long-Term Capital Gains Tax Table
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.main.capital_gains
        # the tax for capital gains comes into effect after 2024
        if p.in_effect:
            capital_gains = person("long_term_capital_gains", period)
            filing_status = person.tax_unit(
                "filing_status",
                period,
            )
            rate_threshold = select(
                [
                    filing_status == filing_status.SINGLE,
                    filing_status == filing_status.SEPARATE,
                    filing_status == filing_status.HEAD_OF_HOUSEHOLD,
                    filing_status == filing_status.SURVIVING_SPOUSE,
                ],
                [
                    p.rates.single.thresholds[0],
                    p.rates.separate.thresholds[0],
                    p.rates.head_of_household.thresholds[0],
                    p.rates.surviving_spouse.thresholds[0],
                ],
            )
            applicable_threshold = person(
                "mt_capital_gains_tax_applicable_threshold_indiv", period
            )
            higher_rate_applies = applicable_threshold < 0
            lower_rate = select(
                [
                    filing_status == filing_status.SINGLE,
                    filing_status == filing_status.SEPARATE,
                    filing_status == filing_status.SURVIVING_SPOUSE,
                    filing_status == filing_status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.single.rates[-1],
                    p.rates.separate.rates[-1],
                    p.rates.surviving_spouse.rates[-1],
                    p.rates.head_of_household.rates[-1],
                ],
            )
            higher_rate = select(
                [
                    filing_status == filing_status.SINGLE,
                    filing_status == filing_status.SEPARATE,
                    filing_status == filing_status.SURVIVING_SPOUSE,
                    filing_status == filing_status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.single.rates[0],
                    p.rates.separate.rates[0],
                    p.rates.surviving_spouse.rates[0],
                    p.rates.head_of_household.rates[0],
                ],
            )
            # Calculate taxes
            base_capital_gains_tax = lower_rate * rate_threshold
            capital_gains_main_tax = higher_rate * capital_gains

            # Calculate lower capital gains tax
            lower_capital_gains_tax = where(
                capital_gains <= rate_threshold,
                capital_gains * lower_rate,
                base_capital_gains_tax
                + (capital_gains - rate_threshold) * higher_rate,
            )
            return where(
                higher_rate_applies,
                capital_gains_main_tax,
                lower_capital_gains_tax,
            )
        return 0
