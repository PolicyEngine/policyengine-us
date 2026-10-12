from policyengine_us.model_api import *


class wy_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity eligible for Wyoming Child Care, Purchase of Service"
    definition_period = MONTH
    defined_for = StateCode.WY
    reference = (
        "https://rules.wyo.gov/DownloadFile.aspx?source_id=24638&source_type_id=81&doc_type_id=110&include_meta_data=Y&file_type=pdf&filename=24638.pdf&token=189087205215053222164006221008072207044097222254",  # Wyo. Admin. Rules, DFS, Child Care - Purchase of Service, Ch. 1 §8(e)(i)(C)-(E), (I), §9(g)(ii), eff. 05/07/2025 (PDF pp. 16-17, 24)
        "https://dfs.wyo.gov/about/policy-manuals/child-care-subsidy-policy-manual/",  # Wyoming DFS Child Care Subsidy Policy Manual §1101.E (PDF p. 1)
    )

    def formula(spm_unit, period, parameters):
        # Rules Ch. 1 §8(e)(i)(C), (D): every caretaker (parent and spouse)
        # must participate in an approved activity, generally for the same
        # hours; Wyoming sets no minimum-hours floor for employment or
        # education, so any work hours qualify. §8(e)(i)(E): when one
        # caretaker is disabled and unable to care for the child, the other
        # caretaker's employment qualifies the unit (is_disabled proxies the
        # medical-verification requirement we don't track). POWER recipients
        # meet the POWER work requirement, itself an approved activity
        # (Manual §502). meets_ccdf_activity_test is a fallback input for
        # approved activities not individually modeled: employment training,
        # education and high school equivalency, SNAP E&T, temporary job
        # search (three months at up to 20 hours per week), and sleep time
        # between shifts. §8(e)(i)(I): self-employment outside the home
        # counts as employment for this test, with no minimum-hours floor.
        # Rules §9(g)(ii) / Manual §1101.E cap a self-employed caretaker's
        # authorized care hours at monthly net self-employment income
        # divided by the federal minimum wage (before the earned income
        # disregard); authorized hours are not computed here — care hours
        # are supplied through the childcare_hours_per_day input that
        # drives the part-day or full-day rate (wy_ccap_day_length).
        person = spm_unit.members
        # Rules Ch. 1 §6(f) lets a minor parent apply on their own behalf,
        # and §8(e)(i)(K) qualifies a minor parent living with their own
        # caretakers when all of them participate in an approved activity.
        # is_tax_unit_head_or_spouse is structurally False for anyone under
        # 18, so the caretaker set also includes minor parents (a person
        # under 18 with their own child in the household).
        is_minor_parent = person("is_child", period.this_year) & person(
            "is_parent", period.this_year
        )
        is_caretaker = (
            person("is_tax_unit_head_or_spouse", period.this_year) | is_minor_parent
        )
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        working = is_caretaker & (hours > 0)
        waived = is_caretaker & person("is_disabled", period.this_year)
        idle = is_caretaker & ~working & ~waived
        # Every non-disabled caretaker must work, and at least one caretaker
        # must work, so a unit whose only caretakers are idle and disabled
        # does not qualify through the disability exception.
        every_able_caretaker_works = spm_unit.sum(idle) == 0
        any_caretaker_works = spm_unit.sum(working) > 0
        work_eligible = every_able_caretaker_works & any_caretaker_works
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return work_eligible | tanf_enrolled | fallback
