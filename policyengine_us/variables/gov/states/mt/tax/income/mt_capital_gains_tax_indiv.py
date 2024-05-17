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
            filing_status = person.tax_unit(
                "state_filing_status_if_married_filing_separately_on_same_return",
                period,
            )
            status = filing_status.possible_values
            non_qualified_income = max_(taxable_income - capital_gains, 0)
            non_qualified_income_exceeds_threshold = (
                non_qualified_income > p.threshold[filing_status]
            )
            # When the nonqualified income exceeds the threshold, apply the main rate
            capital_gains_main_tax = (
                p.rates.main[filing_status] * capital_gains
            )
            lower_threshold = max_(
                p.threshold[filing_status] - non_qualified_income, 0
            )
            base_rate = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.single.calc(0),
                    p.rates.separate.calc(0),
                    p.rates.widow.calc(0),
                    p.rates.head_of_household.calc(0),
                ],
            )
            lower_rate = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.lower.single,
                    p.rates.lower.separate,
                    p.rates.lower.widow,
                    p.rates.lower.head_of_household,
                ],
            )
            base_capital_gains_tax = base_rate * lower_threshold
            lower_capital_gains_tax = where(
                capital_gains <= lower_threshold,
                capital_gains
                * base_rate,  # First capital gians below the lower threshold
                base_capital_gains_tax
                + (capital_gains - lower_threshold)
                * lower_rate,  # capitals gains over the lower threshold
            )

            capital_gains_tax = where(
                non_qualified_income_exceeds_threshold,
                capital_gains_main_tax,
                lower_capital_gains_tax,
            )
            return capital_gains_tax
        else:
            return 0
