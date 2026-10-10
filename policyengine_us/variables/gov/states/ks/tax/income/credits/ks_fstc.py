from policyengine_us.model_api import *


class ks_fstc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas food sales tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip22.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip23.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip24.pdf#page=6",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.credits
        # A return on which the filer (or, if joint, either spouse) can be
        # claimed has no dependents (IRC 152(b)(1)): the K-40 dependent count is
        # "0" and no child is claimed "as a personal exemption".
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        # determine if tax unit is eligible for credit
        person = tax_unit.members
        # ... any child dependents?
        count_all_dependents = where(
            filer_is_dependent, 0, tax_unit("tax_unit_dependents", period)
        )
        child_age = p.food_sales_tax.child_age
        is_child = person("age", period) < child_age
        is_child_dependent = person("is_tax_unit_dependent", period) & is_child
        count_child_dependents = where(
            filer_is_dependent, 0, tax_unit.sum(is_child_dependent)
        )
        has_eligible_child = count_child_dependents > 0
        # ... any elderly adults?
        min_adult_age = p.food_sales_tax.min_adult_age
        elderly_head = tax_unit("age_head", period) >= min_adult_age
        elderly_spouse = tax_unit("age_spouse", period) >= min_adult_age
        eligible_age = elderly_head | elderly_spouse
        # ... any adult disabilities?
        eligible_blind_disabled = (
            tax_unit("blind_head", period)
            | tax_unit("blind_spouse", period)
            | tax_unit("head_is_disabled", period)
            | tax_unit("spouse_is_disabled", period)
        )
        # ... any eligibility for credit?
        eligible_unit = has_eligible_child | eligible_age | eligible_blind_disabled
        # determine if income eligible for credit
        fagi = tax_unit("adjusted_gross_income", period)
        eligible_income = fagi <= p.food_sales_tax.agi_limit
        # compute credit amount
        eligible = eligible_unit & eligible_income
        # Line E is the "total number of exemptions" from the front of the
        # K-40. Through 2023 a claimed filer enters "0" there; from 2024 the
        # filing-status exemptions remain and only the dependent count is "0".
        exemption_regime = parameters(period).gov.states.ks.tax.income.exemptions
        filers = tax_unit("head_spouse_count", period)
        claimed_filer_exemptions = where(
            exemption_regime.by_filing_status.in_effect, filers, 0
        )
        exemptions = where(
            filer_is_dependent,
            claimed_filer_exemptions,
            tax_unit("tax_unit_size", period),
        )
        old_dependents = count_all_dependents - count_child_dependents
        fstc_exemptions = max_(0, exemptions - old_dependents)
        return eligible * fstc_exemptions * p.food_sales_tax.amount
