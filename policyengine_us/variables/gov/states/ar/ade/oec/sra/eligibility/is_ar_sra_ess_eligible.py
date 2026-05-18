from policyengine_us.model_api import *


class is_ar_sra_ess_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Arkansas SRA Employment-Sponsored Subsidy (ESS) track"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=16"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.eligibility
        was_tea = spm_unit("ar_was_tea_recipient", period.this_year)
        months_since = spm_unit("ar_months_since_tea_exit", period)
        ar_tea = spm_unit("ar_tea", period)
        within_window = (months_since > 0) & (months_since <= p.ess_window_months)
        in_track = was_tea & (ar_tea == 0) & within_window
        in_year_1 = months_since <= p.ess_year_1_window_months
        person = spm_unit.members
        is_adult = person("age", period.this_year) >= p.adult_age_threshold
        hours = person("weekly_hours_worked", period.this_year)
        adult_hours = where(is_adult, hours, 0)
        max_adult_hours = spm_unit.max(adult_hours)
        adult_is_student = is_adult & person(
            "is_full_time_college_student", period.this_year
        )
        any_adult_student = spm_unit.sum(adult_is_student) > 0
        # FSU §4.1.5.1 Year-1 alt path: earnings make family TEA-income-ineligible.
        tea_income_ineligible = ~spm_unit("ar_tea_income_eligible", period)
        year_1_active = (
            (max_adult_hours >= p.activity_hours_ess_year_1)
            | any_adult_student
            | tea_income_ineligible
        )
        year_2_active = (
            max_adult_hours >= p.activity_hours_ess_year_2
        ) | any_adult_student
        activity_ok = where(in_year_1, year_1_active, year_2_active)
        return in_track & activity_ok
