from policyengine_us.model_api import *


class is_snap_alien_military_connected(Variable):
    value_type = bool
    entity = Person
    label = "Has a military connection exempting an alien from the SNAP waiting period"
    documentation = (
        "Whether the person has a military connection under 8 USC "
        "1612(a)(2)(C) and 7 CFR 273.4(a)(6)(ii)(G): a veteran or active duty "
        "member of the Armed Forces, the spouse of one (linked through the "
        "marital unit), or an unmarried dependent child of one (a tax unit "
        "dependent who is under 18, a full-time student under 22, or "
        "disabled, whose tax unit head or spouse served). is_veteran and "
        "is_military stand in for the service test and are broader than it. "
        "SNAP requires an honorable discharge for reasons other than alien "
        "status plus the minimum active duty service of 38 USC 5303A(d); a "
        "discharge under honorable conditions does not qualify (FNS October "
        "31, 2025 memo, Attachment 2). is_veteran uses the 38 USC 101(2) "
        "'other than dishonorable' standard and by default is true for "
        "anyone receiving veterans_benefits, which can include survivors and "
        "misses veterans without VA income. is_military does not exclude the "
        "National Guard or active duty for training. Tax unit dependency "
        "stands in for an unmarried dependent child and can include "
        "stepchildren, grandchildren and other dependents, and is_disabled "
        "stands in for a child who was disabled and dependent before age 18. "
        "On balance these proxies over-grant the exemption, which "
        "under-applies the waiting period. Not modeled: the unremarried "
        "surviving spouse of a deceased veteran and the child of a deceased "
        "veteran who was dependent at the veteran's death. Set this variable "
        "directly to override the proxies."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1612#a_2_C",
        "https://www.law.cornell.edu/uscode/text/8/1613#b_2",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_ii_G",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility.pdf#page=11",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.usda.snap.eligibility.waiting_period.exceptions.military
        # 7 CFR 273.4(a)(6)(ii)(G)(1)-(2): veteran or active duty member.
        served = person("is_veteran", period) | person("is_military", period)
        # 7 CFR 273.4(a)(6)(ii)(G)(3): the marital unit holds the person and
        # their spouse, so this covers the member and the member's spouse.
        self_or_spouse_served = person.marital_unit.any(served)
        # 7 CFR 273.4(a)(6)(ii)(G)(3): unmarried dependent child under 18, a
        # full-time student under 22, or a disabled child.
        age = person("age", period)
        full_time_student = person("is_full_time_student", period)
        dependent_child = person("is_tax_unit_dependent", period) & (
            (age < p.child_age_threshold)
            | (full_time_student & (age < p.student_age_threshold))
            | person("is_disabled", period)
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        parent_served = person.tax_unit.any(served & head_or_spouse)
        return self_or_spouse_served | (dependent_child & parent_served)
