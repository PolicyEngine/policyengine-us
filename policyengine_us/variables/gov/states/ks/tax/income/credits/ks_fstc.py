from policyengine_us.model_api import *


class ks_fstc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas food sales tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.credits
        # determine if tax unit is eligible for credit
        person = tax_unit.members
        # ... any child dependents?
        count_all_dependents = tax_unit("tax_unit_dependents", period)
        child_age = p.food_sales_tax.child_age
        is_child = person("age", period) < child_age
        is_child_dependent = person("is_tax_unit_dependent", period) & is_child
        count_child_dependents = tax_unit.sum(is_child_dependent)
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
        eligible_unit = (
            has_eligible_child | eligible_age | eligible_blind_disabled
        )
        # determine if income eligible for credit
        fagi = tax_unit("adjusted_gross_income", period)
        eligible_income = fagi <= p.food_sales_tax.agi_limit
        # compute credit amount
        eligible = eligible_unit & eligible_income
        exemptions = tax_unit("ks_count_exemptions", period)
        old_dependents = count_all_dependents - count_child_dependents
        fstc_exemptions = max_(0, exemptions - old_dependents)
        return eligible * fstc_exemptions * p.food_sales_tax.amount
