from policyengine_us.model_api import *


class mt_income_tax_before_2021_rebate(Variable):
    value_type = float
    entity = Person
    label = "Montana income tax before refundable credits and the 2021 rebate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    # Each column's share of Form 2 line 20 (income tax before refundable
    # credits) before the 2021 income tax rebate, used only to cap the reported
    # rebate at the 2021 liability (MCA 15-30-2191(2)). Montana treated married
    # couples who filed separately (status 2a) as separate individuals, so a
    # column filing separately is capped at its own line 20; a return filed
    # jointly shares the return's line 20 across the head and spouse columns so
    # their pooled rebate is capped at the joint liability. The separate-vs-
    # joint choice is made on the rebate-free liabilities to avoid a cycle
    # through the rebate itself: this is a reporting cap that does not enter the
    # tax calculation (taxsim #1189).
    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        capital_gain_credit = person("mt_capital_gain_credit", period)
        # Separately-filed column: own line 20 (before the rebate).
        indiv_before_credits = person(
            "mt_income_tax_before_non_refundable_credits_indiv", period
        )
        indiv_line_20 = max_(indiv_before_credits - capital_gain_credit, 0)
        # Jointly-filed return: the return's line 20, shared evenly across the
        # head and spouse columns claiming the rebate.
        joint_before_credits = person.tax_unit(
            "mt_income_tax_before_non_refundable_credits_joint", period
        )
        joint_capital_gain_credit = person.tax_unit.sum(capital_gain_credit)
        joint_line_20 = max_(joint_before_credits - joint_capital_gain_credit, 0)
        claimants = person.tax_unit.sum(head_or_spouse)
        joint_share = where(claimants > 0, joint_line_20 / claimants, 0)
        # The couple files separately when doing so lowers the rebate-free
        # liability, mirroring mt_files_separately without depending on the
        # rebate (which would create a cycle).
        indiv_line_20_unit = person.tax_unit.sum(indiv_line_20)
        p = parameters(period).gov.states.mt.tax.income
        separate_allowed = p.married_filing_separately_on_same_return_allowed
        cheaper_separately = indiv_line_20_unit < joint_line_20
        files_separately = separate_allowed & cheaper_separately
        return where(files_separately, indiv_line_20, joint_share)
