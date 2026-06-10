from policyengine_us.model_api import *


class ks_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.KS
    reference = "https://content.dcf.ks.gov/ees/keesm/Current/keesm6000.htm"

    def formula(spm_unit, period, parameters):
        # KEESM 6410 (Children's Earnings): "the earnings of any child under age
        # 18 (or age 19 if the child is working toward the attainment of a high
        # school diploma or its equivalent) are exempt unless the child is
        # legally responsible for another person in the nuclear family." Count
        # earned income for members aged 18+ and for any minor who is a parent
        # (is_parent, i.e. has their own child in the household — legally
        # responsible for another nuclear-family member), so a teen parent's own
        # wages stay countable. We don't model the high-school-diploma extension
        # to age 19 at the moment. Unearned income is counted for all members.
        p = parameters(period).gov.states.ks.dcf.ccap.income.countable_income
        person = spm_unit.members
        is_adult = person("age", period.this_year) >= 18
        is_minor_parent = person("is_parent", period.this_year)
        earnings_counted = is_adult | is_minor_parent
        earned_per_person = add(person, period, p.earned)
        earned_income = spm_unit.sum(earned_per_person * earnings_counted)
        unearned_income = add(spm_unit, period, p.unearned)
        return earned_income + unearned_income
