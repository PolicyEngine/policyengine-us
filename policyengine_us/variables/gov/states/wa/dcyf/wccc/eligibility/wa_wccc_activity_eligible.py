from policyengine_us.model_api import *


class wa_wccc_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity eligible for Washington WCCC"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0020",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        has_earnings = person("earned_income", period.this_year) > 0
        is_student = person("is_full_time_student", period.this_year)
        # WAC 110-15-0020(2)(b) waives the approved-activity requirement for
        # a parent who is medically incapacitated. The household passes if
        # every parent has either an approved activity or a waiver.
        # We don't track approved-activity hours at the moment; treat any
        # earnings or student status as meeting the activity test.
        is_disabled = person("is_disabled", period.this_year)
        individually_eligible = has_earnings | is_student | is_disabled
        return spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
