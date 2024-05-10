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
            taxable_income = person("mt_taxable_income_indiv", period)
            non_qualified_income = max_(taxable_income - capital_gains, 0)

            filing_status = person.tax_unit(
                "state_filing_status_if_married_filing_separately_on_same_return",
                period,
            )
            status = filing_status.possible_values
            capital_gains_rate, base_rate = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.single.calc(taxable_income),
                    p.rates.single.calc(0),
                    p.rates.separate.calc(taxable_income),
                    p.rates.separate.calc(0),
                    p.rates.widow.calc(taxable_income),
                    p.rates.widow.calc(0),
                    p.rates.head_of_household.calc(taxable_income),
                    p.rates.head_of_household.calc(0),
                ],
            )
            non_qualified_income_gap = (
                p.threshold[filing_status] - non_qualified_income
            )
            # If the capital gains is over the gap, the gap income will be calculated by the base rate.
            base_tax = non_qualified_income_gap * base_rate
            reduced_capital_gains = max_(
                capital_gains - non_qualified_income_gap, 0
            )
            # Where non_qualified_income is over the threshold, the capital gains tax rate will be the higher rate
            capital_gains_over_threshold = capital_gains * capital_gains_rate
            # Equally judged by whether the taxable income is under the threshold
            capital_gains_under_threshold = (
                capital_gains <= non_qualified_income_gap
            )
            reduced_capital_gains_tax = where(
                capital_gains_under_threshold,
                capital_gains
                * capital_gains_rate,  # capital_gains within the gap
                base_tax
                + reduced_capital_gains
                * capital_gains_rate,  # capital gains over the gap
            )
            nonqualified_income_over_threshold = non_qualified_income_gap < 0

            return where(
                nonqualified_income_over_threshold,
                capital_gains_over_threshold,
                reduced_capital_gains_tax,
            )
        else:
            return 0
