from policyengine_us.model_api import *


class military_retirement_pay(Variable):
    value_type = float
    entity = Person
    label = "Military retirement pay"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Taxable retirement pay received by former members of the uniformed services "
        "of the United States, meaning after the Survivor Benefit Plan (SBP) premium reduction, "
        "and excluding Combat-Related Special Compensation (CRSC) and disability retirement pay "
        "excludable under 26 U.S.C. § 104 (see IRS Pub 525 (2024), p. 16). Excludable amounts "
        "such as CRSC and VA Dependency and Indemnity Compensation (DIC) should be reported "
        "under veterans_benefits. Included in federal gross income under 26 U.S.C. § 61(a)(10).\n\n"
        "Known limitations:\n"
        "- Montana (MCA 15-30-2120(3)(n)): allows a deduction of up to 50% of military retired pay "
        "(capped at Montana earned income) starting in 2024; this deduction is not yet modeled.\n"
        "- North Carolina (N.C. Gen. Stat. § 105-153.5(b)(5a)): deduction requires either 20 years of military "
        "service or medical retirement; entering military_retirement_pay alone without service record "
        "variables (years_in_military or is_permanently_disabled_veteran) defaults to no deduction."
    )
    reference = (
        "https://militarypay.defense.gov/Pay/Retirement/",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=16",
    )
    uprating = "calibration.gov.irs.soi.taxable_pension_income"
