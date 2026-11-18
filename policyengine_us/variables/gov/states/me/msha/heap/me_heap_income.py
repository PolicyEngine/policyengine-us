from policyengine_us.model_api import *


class me_heap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Maine HEAP household income"
    defined_for = StateCode.ME
    reference = (
        # PDF pages 11-15
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=11",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/346c024.docx",
        # PDF pages 6-7
        "https://liheapch.acf.gov/docs/2026/state-plans/ME_Plan_2026.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.me.msha.heap.income
        person = spm_unit.members
        # Gross income of members of every immigration status (rule 3(C)(1)).
        # Each source is floored at zero, so a loss in one source cannot offset
        # another.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period), 0)
        # Earnings of a full-time high school student are excluded unless the
        # student is the primary applicant, represented by the tax unit head.
        excluded_student = person("is_in_k12_school", period) & ~person(
            "is_tax_unit_head", period
        )
        counted = where(excluded_student, 0, earned) + unearned
        adult = person("age", period) >= p.minimum_age
        # Rule 3(C)(1) counts income from all sources unless excluded, and no
        # exclusion names TANF. The annual tanf aggregate includes me_tanf and
        # applies take-up; me_tanf alone is the entitlement a nonrecipient
        # could get. The household grant is counted once, not once per member.
        gross = spm_unit.sum(counted * adult) + spm_unit("tanf", period)
        # A household over the income limit deducts medical expenses, but only
        # the amount needed to reach the limit.
        limit = spm_unit("me_heap_income_limit", period)
        medical = add(spm_unit, period, p.medical_expense_sources)
        return where(gross > limit, max_(gross - medical, limit), gross)
