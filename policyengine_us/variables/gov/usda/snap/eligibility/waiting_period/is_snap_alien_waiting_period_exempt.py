from policyengine_us.model_api import *


class is_snap_alien_waiting_period_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Exempt from the SNAP qualified alien waiting period"
    documentation = (
        "Whether a qualified alien meets an exception to the SNAP five-year "
        "waiting period under 7 CFR 273.4(a)(6)(ii) and 8 USC 1612(a)(2). "
        "Modeled exceptions: under 18 ((ii)(J)); receiving blindness or "
        "disability benefits as specified in 7 CFR 271.2 ((ii)(H)), via "
        "is_usda_disabled, which counts any SSI receipt, including age-based "
        "SSI, and does not apply SSI's own noncitizen restrictions to "
        "computed SSI; a military connection via "
        "is_snap_alien_military_connected ((ii)(G)); and, for lawful "
        "permanent residents only, 40 qualifying quarters ((ii)(A)) or "
        "adjustment to lawful permanent residence from a status exempt from "
        "the waiting period ((iv)). Each category stands alone ((iv)), so a "
        "parolee with 40 quarters or a prior exempt status stays subject. "
        "Not modeled, so the waiting period is over-applied to these groups "
        "when years_since_us_entry is below the threshold: people lawfully "
        "residing in the United States on August 22, 1996, and born on or "
        "before August 22, 1931 ((ii)(I)); American Indians born in Canada "
        "and members of federally recognized tribes (8 USC 1612(a)(2)(G)); "
        "Hmong and Highland Laotian tribe members and their families (8 USC "
        "1612(a)(2)(K)); the unremarried surviving spouse and dependent "
        "child of a deceased veteran; and the historic August 22, 1996 "
        "residence conditions on the under-18 and disability exceptions."
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1612#a_2",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_ii",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_iv",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=3",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=4",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.eligibility.waiting_period.exceptions
        # 8 USC 1612(a)(2)(J); 7 CFR 273.4(a)(6)(ii)(J).
        child = person("monthly_age", period) < p.child_age_threshold
        # 8 USC 1612(a)(2)(F)(ii); 7 CFR 273.4(a)(6)(ii)(H) and 271.2.
        disability_benefits = person("is_usda_disabled", period.this_year)
        # 8 USC 1612(a)(2)(C); 7 CFR 273.4(a)(6)(ii)(G).
        military = person("is_snap_alien_military_connected", period.this_year)
        status = person("immigration_status", period.this_year)
        lpr = status == status.possible_values.LEGAL_PERMANENT_RESIDENT
        # 8 USC 1612(a)(2)(B), 1645; 7 CFR 273.4(a)(6)(ii)(A).
        quarters = person("snap_alien_qualifying_quarters", period.this_year)
        has_qualifying_quarters = quarters >= p.qualifying_quarters
        # 7 CFR 273.4(a)(6)(iv); FNS Question and Answer #1 REVISED, Question 5.
        adjusted = person("lpr_adjusted_from_bar_exempt_status", period.this_year)
        lpr_exempt = lpr & (has_qualifying_quarters | adjusted)
        return child | disability_benefits | military | lpr_exempt
