from policyengine_us.model_api import *


class mt_capital_gains_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana net long-term capital gains tax when married couples file separately"
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
                "state_filing_status_if_married_filing_separately_on_same_return",
                period,
            )
            applicable_threshold = person(
                "mt_capital_gains_tax_applicable_threshold_indiv", period
            )
            status = filing_status.possible_values

            lower_rate = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.single.amounts[0],
                    p.rates.separate.amounts[0],
                    p.rates.surviving_spouse.amounts[0],
                    p.rates.head_of_household.amounts[0],
                ],
            )
            higher_rate = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.single.amounts[-1],
                    p.rates.separate.amounts[-1],
                    p.rates.surviving_spouse.amounts[-1],
                    p.rates.head_of_household.amounts[-1],
                ],
            )
            # Calculate taxes
            capital_gains_below_threshold = min_(
                applicable_threshold, capital_gains
            )
            capital_gains_above_threshold = max_(
                capital_gains - applicable_threshold, 0
            )

            lower_capital_gains_tax = (
                capital_gains_below_threshold * lower_rate
            )
            higher_capital_gains_tax = (
                capital_gains_above_threshold * higher_rate
            )

            return lower_capital_gains_tax + higher_capital_gains_tax

        return 0
