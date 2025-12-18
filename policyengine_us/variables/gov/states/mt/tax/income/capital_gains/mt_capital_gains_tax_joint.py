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
            # Line instructions from the 2024 Montana Individual Income Tax Return Form 2
            # https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=2
            # Line 1
            taxable_income = person("mt_taxable_income_joint", period)
            # Line 2
            capital_gains = person("long_term_capital_gains", period)
            # No tax on zero or negative capital gains
            # Line 3
            lesser_of_cg_and_taxable_income = min_(
                capital_gains, taxable_income
            )
            # Line 4
            excess_over_taxable_income = max_(
                taxable_income - lesser_of_cg_and_taxable_income, 0
            )
            filing_status = person.tax_unit("filing_status", period)
            # Line 5
            applicable_threshold = person(
                "mt_capital_gains_tax_applicable_threshold_joint", period
            )
            status = filing_status.possible_values

            lower_rate = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.JOINT,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.single.amounts[0],
                    p.rates.separate.amounts[0],
                    p.rates.joint.amounts[0],
                    p.rates.surviving_spouse.amounts[0],
                    p.rates.head_of_household.amounts[0],
                ],
            )
            higher_rate = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.JOINT,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.rates.single.amounts[-1],
                    p.rates.separate.amounts[-1],
                    p.rates.joint.amounts[-1],
                    p.rates.surviving_spouse.amounts[-1],
                    p.rates.head_of_household.amounts[-1],
                ],
            )
            # Line 6
            excess_over_threshold = max_(
                applicable_threshold - excess_over_taxable_income, 0
            )
            # Line 7
            capital_gains_below_threshold = min_(
                excess_over_threshold, lesser_of_cg_and_taxable_income
            )
            # Line 8
            lower_capital_gains_tax = (
                capital_gains_below_threshold * lower_rate
            )
            # Line 9
            income_above_threshold = max_(
                lesser_of_cg_and_taxable_income - excess_over_threshold, 0
            )
            # Line 10
            higher_capital_gains_tax = income_above_threshold * higher_rate
            # Line 11
            return max_(lower_capital_gains_tax + higher_capital_gains_tax, 0)
            # Only apply tax if capital gains are positive

        return 0
