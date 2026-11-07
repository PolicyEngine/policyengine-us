from policyengine_us.model_api import *


class ga_caps_priority_group_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Belongs to a Georgia CAPS priority group"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=1",
        "https://www.decal.ga.gov/documents/attachments/fundingrestrictionsqa.pdf#page=1",
        "https://www.decal.ga.gov/documents/attachments/CCDFStatePlan25-27.pdf#page=25",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixA-CAPS%20Maximum%20Income%20Limits%20by%20Family%20Size.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.priority_groups
        if not p.in_effect:
            return np.ones_like(spm_unit("spm_unit_size", period.this_year), dtype=bool)
        person = spm_unit.members
        # Groups that turn on a child: Child Protective Services and court-ordered
        # supervision (CAPS/00-7, 7.4), need to protect (7.15), DFCS custody (7.5),
        # disabilities (7.7) and Georgia's Pre-K (7.8).
        protective_care = person(
            "receives_or_needs_protective_services", period.this_year
        ) | person("is_under_court_supervision", period.this_year)
        dfcs_custody = person("is_in_foster_care", period)
        disability = person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
        pre_k = person("ga_caps_pre_k_enrolled", period)
        child_group = spm_unit.any(
            person("ga_caps_eligible_child", period)
            & (protective_care | dfcs_custody | disability | pre_k)
        )
        # Groups that turn on a parent: minor parents (7.14) and student parents
        # (7.16). is_full_time_student stands in for enrollment in the listed
        # programs, as it does in ga_caps_activity_eligible.
        minor_parent = person("age", period.this_year) <= p.minor_parent_age
        student_parent = (
            person("is_full_time_student", period.this_year)
            & p.student_parent_in_effect
        )
        parent_group = spm_unit.any(
            person("is_tax_unit_head_or_spouse", period.this_year)
            & (minor_parent | student_parent)
        )
        # 7.12 and Appendix A: gross applicable income against an annual chart.
        # Round to cents so floating-point noise can't move a family at the limit.
        annual_income = np.round(
            spm_unit("ga_caps_countable_income", period) * MONTHS_IN_YEAR, 2
        )
        very_low_income_limit = np.round(
            spm_unit("spm_unit_fpg", period.this_year) * p.very_low_income_fpg_rate, 2
        )
        very_low_income = annual_income <= very_low_income_limit
        # is_tanf_enrolled stands in for families in TANF employment services
        # (7.9); the group excludes payees outside those services, and the model
        # can't tell them apart.
        return (
            child_group
            | parent_group
            | very_low_income
            | spm_unit("is_tanf_enrolled", period)
            | spm_unit.household("is_homeless", period.this_year)
            | spm_unit("ga_caps_domestic_violence", period)
            | spm_unit("ga_caps_natural_disaster", period)
            | spm_unit("ga_caps_grandparents_raising_grandchildren", period)
        )
