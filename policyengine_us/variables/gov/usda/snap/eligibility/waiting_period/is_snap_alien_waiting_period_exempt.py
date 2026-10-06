from policyengine_us.model_api import *


class is_snap_alien_waiting_period_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Exempt from the SNAP qualified alien waiting period"
    documentation = (
        "Whether a qualified alien meets an exception to the SNAP five-year "
        "waiting period under 7 CFR 273.4(a)(6)(ii) and 8 USC 1612(a)(2). "
        "Modeled exceptions: under 18 ((ii)(J)); receiving benefits for "
        "blindness or disability as specified in 7 CFR 271.2 ((ii)(H)); a "
        "military connection via is_snap_alien_military_connected ((ii)(G)); "
        "and, for lawful permanent residents only, 40 qualifying quarters "
        "((ii)(A)) or admission in, or adjustment from, an exempt category "
        "via is_snap_lpr_in_waiting_period_exempt_category ((ii)(B)-(F), "
        "(iv)). The disability exception reads is_usda_disabled, the "
        "benefit-receipt test of 7 CFR 271.2 paragraphs (2)-(11) that SNAP "
        "uses for its elderly or disabled member rules. That test counts any "
        "SSI receipt, including SSI paid on the basis of age. 8 USC "
        "1612(a)(2)(F)(ii) says 'benefits or assistance for blindness or "
        "disability', which could support a narrower reading. The model "
        "follows the definition that provision cross-references: 7 USC "
        "2012(j)(2)(A) lists SSI receipt with no disability condition, while "
        "(2)(B) and (3) carry one. It also follows the 2010 final rule, "
        "which extends the exception to every qualified alien who meets that "
        "definition (75 FR 4915). Like other SNAP uses of is_usda_disabled, "
        "receipt in any month of the year counts for every month of that "
        "year. Blindness or disability without a benefit does not exempt. "
        "Computed SSI applies SSI's qualified noncitizen list and its lawful "
        "permanent resident 40-quarter test (ssi_qualifying_quarters_earnings, "
        "default 40) but not SSI's own five-year bar (8 USC 1613). Computed "
        "SSI also pays parolees and conditional entrants whom 8 USC "
        "1612(a)(1) generally denies SSI. So computed SSI can exempt a recent "
        "entrant whom SSI's rules would deny; supply ssi or receives_ssi to "
        "avoid this. Each category stands alone ((iv)), so a parolee with 40 "
        "quarters or a prior exempt status stays subject. Not modeled, so the "
        "waiting period is over-applied to these groups when "
        "years_since_us_entry is below the threshold: people lawfully "
        "residing in the United States on August 22, 1996, and born on or "
        "before August 22, 1931 ((ii)(I)); American Indians born in Canada "
        "and members of federally recognized tribes (8 USC 1612(a)(2)(G)) and "
        "Hmong and Highland Laotian tribe members and their families (8 USC "
        "1612(a)(2)(K)) who are not lawful permanent residents (those who "
        "are lawful permanent residents are exempt when "
        "is_snap_lpr_in_waiting_period_exempt_category is set); the "
        "unremarried surviving spouse and dependent child of a deceased "
        "veteran; and the historic August 22, 1996 residence conditions on "
        "the under-18 and disability exceptions."
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1612#a_2",
        "https://www.law.cornell.edu/uscode/text/8/1612#a_2_F_ii",
        "https://www.law.cornell.edu/uscode/text/7/2012#j",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_ii",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_iv",
        "https://www.law.cornell.edu/cfr/text/7/271.2",
        "https://www.govinfo.gov/content/pkg/FR-2010-01-29/pdf/2010-815.pdf#page=4",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=3",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=4",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=5",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.eligibility.waiting_period.exceptions
        year = period.this_year
        # 8 USC 1612(a)(2)(J); 7 CFR 273.4(a)(6)(ii)(J).
        child = person("monthly_age", period) < p.child_age_threshold
        # 8 USC 1612(a)(2)(F)(ii); 7 USC 2012(j); 7 CFR 273.4(a)(6)(ii)(H)
        # and 271.2: receipt of a benefit listed in gov.usda.disabled_programs.
        disability_benefits = person("is_usda_disabled", year)
        # 8 USC 1612(a)(2)(C); 7 CFR 273.4(a)(6)(ii)(G).
        military = person("is_snap_alien_military_connected", year)
        status = person("immigration_status", year)
        lpr = status == status.possible_values.LEGAL_PERMANENT_RESIDENT
        # 8 USC 1612(a)(2)(B), 1645; 7 CFR 273.4(a)(6)(ii)(A).
        quarters = person("snap_alien_qualifying_quarters", year)
        has_qualifying_quarters = quarters >= p.qualifying_quarters
        # 7 CFR 273.4(a)(6)(ii)(B)-(F) and (iv); FNS Question and Answer #1
        # REVISED, Question 5.
        exempt_category = person("is_snap_lpr_in_waiting_period_exempt_category", year)
        lpr_exempt = lpr & (has_qualifying_quarters | exempt_category)
        return child | disability_benefits | military | lpr_exempt
