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
            non_qualified_income_gap = (
                p.threshold[filing_status] - non_qualified_income
            )
            lower_base_tax = (
                non_qualified_income_gap
                * p.rates.reduced_capital_gains.lower[filing_status]
            )
            capital_gains_under_threshold = (
                capital_gains <= non_qualified_income_gap
            )
            lower_capital_gains_tax = (
                capital_gains
                * p.rates.reduced_capital_gains.lower[filing_status]
            )
            higher_capital_gains_tax = (
                lower_base_tax
                + max_(capital_gains - non_qualified_income_gap, 0)
                * p.rates.reduced_capital_gains.higher[filing_status]
            )
            reduced_capital_gains_tax = where(
                capital_gains_under_threshold,
                lower_capital_gains_tax,
                higher_capital_gains_tax,
            )
            nonqualified_income_over_threshold = non_qualified_income_gap < 0
            capital_gains_over_threshold = (
                capital_gains
                * p.rates.reduced_capital_gains.higher[filing_status]
            )
            return where(
                nonqualified_income_over_threshold,
                capital_gains_over_threshold,
                reduced_capital_gains_tax,
            )
        else:
            return 0
