from policyengine_us.model_api import *


class ky_ktap_dependent_care_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP dependent care disregard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/",
        # PDF pages 162-163
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLIII.pdf#page=162",
    )
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        # NOTE: Full-time/part-time distinction not modeled.
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("age", period.this_year)
        # Children use their age-based rate per 921 KAR 2:016 Section
        # 5(3)(b)2; the older-age zero-out reflects children aging out of
        # care. Incapacitated adults are capped one by one in
        # ky_ktap_incapacitated_adult_care_disregard. Child care expenses are
        # a unit total, so the children's caps are summed.
        is_child_care_recipient = is_dependent & ~incapacitated_adult
        child_caps = spm_unit.sum(p.dependent_care.calc(age) * is_child_care_recipient)
        childcare_expenses = spm_unit("childcare_expenses", period)
        child_care_disregard = min_(childcare_expenses, child_caps)
        # Per Section 5(3)(b)1.c and MS 2840 B.1, child care counts only for a
        # case that is otherwise ineligible without it; CCAP pays child care
        # for a case that remains eligible. The month-of-application case
        # (Section 5(3)(b)1.d) is not modeled.
        child_care_counts = spm_unit(
            "ky_ktap_ineligible_without_child_care_disregard", period
        )
        adult_care_disregard = spm_unit(
            "ky_ktap_incapacitated_adult_care_disregard", period
        )
        return adult_care_disregard + where(child_care_counts, child_care_disregard, 0)
