from policyengine_us.model_api import *


class military_retirement_pay_survivors(Variable):
    value_type = float
    entity = Person
    label = "Military retirement survivor benefit payments"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Taxable survivor annuity payments received by surviving spouses, dependent children, "
        "or other designated annuitants under a United States uniformed services retirement plan "
        "(such as the Survivor Benefit Plan (SBP) or Retired Serviceman's Family Protection Plan). "
        "Excludes tax-exempt payments such as VA Dependency and Indemnity Compensation (DIC), "
        "which should be reported under veterans_benefits (see IRS Pub 525 (2024), p. 16). "
        "Included in federal gross income under 26 U.S.C. § 61(a)(10) and § 72.\n\n"
        "Known limitations:\n"
        "- Montana (MCA 15-30-2120(3)(n)(ii)): allows exempting up to 50% of military survivor benefits "
        "regardless of other income starting in 2024 (Form WMRE); this deduction is not yet modeled.\n"
        "- North Carolina (N.C. Gen. Stat. § 105-153.5(b)(5a)): deduction requires either 20 years of military "
        "service or medical retirement; entering military_retirement_pay_survivors alone without survivor "
        "eligibility variables (nc_military_retirement_survivor_eligible) defaults to no deduction."
    )
    reference = (
        "https://militarypay.defense.gov/Benefits/Survivor-Benefit-Program/",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=16",
        "https://www.irs.gov/publications/p575",
    )
    uprating = "calibration.gov.irs.soi.taxable_pension_income"
