from policyengine_us.model_api import *


class nj_njhps_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for New Jersey Health Plan Savings"
    definition_period = YEAR
    defined_for = StateCode.NJ
    reference = (
        "https://www.cms.gov/files/document/1332-ota-methodology-addendum-nj-pass-through.pdf#page=8",
        "https://pub.njleg.gov/bills/2020/AL20/61_.HTM",
        # DOBI's plan year 2026 schedule, by "Federal Poverty Level Range".
        "https://www.nj.gov/dobi/division_insurance/ihcseh/ratefilings/2027RateFilingRequirements.pdf#page=4",
        # The 600% limit in dollars for one person: $93,900 (600% of the 2025
        # guideline) in DOBI's July 2026 release, and $95,760 (600% of the 2026
        # guideline) for "tax households" on Get Covered NJ during open
        # enrollment for 2027.
        "https://www.nj.gov/dobi/pressreleases/pr260709.html#:~:text=up%20to%20600%20percent%20of%20the%20federal%20poverty%20level",
        "https://www.nj.gov/getcoverednj/financialhelp/premiums/#:~:text=Tax%20households%20with%20annual%20incomes",
    )
    documentation = (
        "A tax unit is eligible for New Jersey Health Plan Savings when the "
        "program is in effect and at least one member is eligible under "
        "nj_njhps_member_eligible, which requires household income (ACA MAGI "
        "per 26 U.S.C. 36B(d)(2)) of at least 138% and at most 600% of the "
        "federal poverty line (aca_fpg, the prior-year guideline for the "
        "section 36B tax family), measured as the exact ratio rather than the "
        "truncated aca_magi_fraction. Households below 138% FPL are routed to "
        "NJ FamilyCare/Medicaid rather than NJHPS; the 138% floor is inclusive "
        "and the 600% ceiling is inclusive. New Jersey residency is enforced "
        "by defined_for."
    )

    def formula(tax_unit, period, parameters):
        in_effect = parameters(period).gov.states.nj.dobi.njhps.in_effect
        # nj_njhps_member_eligible applies the 138-600% income band, so a unit
        # with an eligible member has already passed it.
        has_eligible_member = add(tax_unit, period, ["nj_njhps_member_eligible"]) > 0
        return in_effect & has_eligible_member
