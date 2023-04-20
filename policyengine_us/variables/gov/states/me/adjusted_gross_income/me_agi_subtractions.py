from policyengine_us.model_api import *


class me_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME AGI subtractions"
    unit = USD
    documentation = "Subtractions from ME AGI over federal AGI."
    definition_period = YEAR
    defined_for = StateCode.ME
    dict(
        title="Schedule 1S, Income Subtraction Modifications",
        href="https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf",
    )

    def formula(tax_unit, period, parameters):
        # Taxable social security subtraction for the tax unit
        taxable_ss = add(tax_unit, period, ["taxable_social_security"])

        # Government/bond interest subtraction for the tax unit
        us_govt_interest = tax_unit("us_govt_interest", period)

        # Pension income subtraction for the tax unit
        # If married filing jointly, the deduction is calculated for taxpayer and spouse separately.
        filing_status = tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
        if is_joint == 1:
            # Get eligible non-military pension income for each person in the tax unit
            person = tax_unit.members
            is_head = person("is_tax_unit_head", period)
            is_spouse = person("is_tax_unit_spouse", period)
            pension_income = person("pension_income", period)
            head_pension_income = tax_unit.sum(
                where(is_head, pension_income, 0)
            )
            spouse_pension_income = tax_unit.sum(
                where(is_spouse, pension_income, 0)
            )
            # Get social security and railroad retirement benefits- whether taxable or not - for the tax unit
            gross_ss = person("social_security", period)
            head_gross_ss = tax_unit.sum(where(is_head, gross_ss, 0))
            spouse_gross_ss = tax_unit.sum(where(is_spouse, gross_ss, 0))

            # Get pension income deduction cap
            p = parameters(
                period
            ).gov.states.me.tax.income.agi.subtractions.pension_exclusion
            cap = p.cap

            # Get ME military retirement pay subtractions.
            # Line 6 in the 2022 - Worksheet for Pension Income Deduction in reference.
            mil_retire_pay = person(
                "me_military_retirement_pay_subtractions", period
            )
            head_mil_retire_pay = tax_unit.sum(
                where(is_head, mil_retire_pay, 0)
            )
            spouse_mil_retire_pay = tax_unit.sum(
                where(is_spouse, mil_retire_pay, 0)
            )

            # Calculate pension income deduction
            head_deductible_pensions = (
                min_(max_(cap - head_gross_ss, 0), head_pension_income)
                + head_mil_retire_pay
            )
            spouse_deductible_pensions = (
                min_(max_(cap - spouse_gross_ss, 0), spouse_pension_income)
                + spouse_mil_retire_pay
            )
            deductible_pensions = (
                head_deductible_pensions + spouse_deductible_pensions
            )

            # Other subtractions
            other_subtractions = tax_unit("me_other_subtractions", period)
            return (
                taxable_ss
                + us_govt_interest
                + deductible_pensions
                + other_subtractions
            )
        else:
            person = tax_unit.members
            pension_income = person("pension_income", period)
            gross_ss = person("social_security", period)
            p = parameters(
                period
            ).gov.states.me.tax.income.agi.subtractions.pension_exclusion
            cap = p.cap
            mil_retire_pay = person(
                "me_military_retirement_pay_subtractions", period
            )
            deductible_pensions = (
                min_(max_(cap - gross_ss, 0), pension_income) + mil_retire_pay
            )
            # Other subtractions
            other_subtractions = tax_unit("me_other_subtractions", period)
            return (
                taxable_ss
                + us_govt_interest
                + deductible_pensions
                + other_subtractions
            )
