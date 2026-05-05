from policyengine_us.model_api import *


class nj_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NJ
    reference = "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=23"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap.income.countable_income
        # N.J.A.C. 10:15 does not enumerate an explicit minor-child earnings
        # exclusion the way VA (8VAC20-790-40(H)) and CT (17b-749-05(b)(2)(E))
        # do, and the PolicyEngine model cannot cite an on-point NJ rule.
        # Apply the same conservative minor-earnings filter Virginia uses
        # (`age >= 18`) to the earned-income sources. This matches VA's
        # explicit exclusion and is strictly narrower than counting all
        # household earnings; it is also consistent with the NJ CC-1
        # application form (03/24) Section D, which does not collect
        # minor children's earnings. Unearned income still counts for
        # all SPM-unit members.
        person = spm_unit.members
        # `age` is YEAR-defined; use period.this_year inside this
        # monthly formula to get the annual value instead of age/12.
        is_adult = person("age", period.this_year) >= 18
        earned_per_person = sum(person(source, period) for source in p.earned_sources)
        adult_earned_income = spm_unit.sum(earned_per_person * is_adult)
        unearned_income = add(spm_unit, period, p.unearned_sources)
        return adult_earned_income + unearned_income
