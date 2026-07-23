from policyengine_us.model_api import *


class wi_shares_parent_in_approved_activity(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin Shares parent in an approved activity"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=35",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/1m/a",
    )

    def formula(person, period, parameters):
        # Approved activities include employment and self-employment,
        # education, Wisconsin Works (W-2) participation, and Tribal TANF
        # (Sections 4.8 and 5.1; Wis. Stat. § 49.155(1m)(a)1.-6.). There is
        # no minimum-hours requirement. A self-employment loss still
        # evidences active self-employment. weekly_hours_worked_before_lsr is
        # used instead of weekly_hours_worked to avoid a labor-supply
        # response cycle.
        is_employed = (
            (person("weekly_hours_worked_before_lsr", period.this_year) > 0)
            | (person("employment_income", period) > 0)
            | (person("self_employment_income", period) != 0)
            | (person("sstb_self_employment_income", period) != 0)
        )
        is_student = person("is_full_time_student", period.this_year)
        is_tanf_enrolled = person.spm_unit("is_tanf_enrolled", period)
        return is_employed | is_student | is_tanf_enrolled
