from policyengine_us.model_api import *


class nj_njhps_member_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Member eligible for New Jersey Health Plan Savings"
    definition_period = YEAR
    defined_for = StateCode.NJ
    reference = (
        "https://www.cms.gov/files/document/1332-ota-methodology-addendum-nj-pass-through.pdf#page=8",
        "https://pub.njleg.gov/bills/2020/AL20/61_.HTM",
    )
    documentation = (
        "A person is a New Jersey Health Plan Savings enrollee when they pay an "
        "ACA marketplace premium, do not file a separate return, and household "
        "income (ACA MAGI per 26 U.S.C. 36B(d)(2)) falls within the 138-600% "
        "FPL NJHPS band. This deliberately does NOT reuse is_aca_ptc_eligible: "
        "that variable embeds the federal 400% FPL income cliff (the PY2026 "
        "baseline sets the ptc_income_eligibility 400% threshold to false, so "
        "is_aca_ptc_eligible is False and aca_ptc is 0 above 400% FPL), which "
        "would drop the 400-600% band that NJHPS covers and that is the single "
        "most PY2026-relevant band because federal APTC is $0 there. Instead "
        "the gate reproduces every NON-INCOME component of federal APTC "
        "eligibility via pays_aca_premium (TIN, lawful-presence/immigration "
        "status, no ineligible minimum essential coverage, and the age-based "
        "premium test) plus the married-filing-separately exclusion, and "
        "substitutes NJHPS's own 138-600% FPL income band for the federal 400% "
        "cliff. This mirrors the non-income internals pattern used for the "
        "above-400% bands in New Mexico and Washington."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.dobi.njhps
        # aca_magi_fraction is a TaxUnit variable read at the person level.
        magi_fraction = person.tax_unit("aca_magi_fraction", period)
        # pays_aca_premium is a Person-level test with no income component:
        # TIN, immigration/lawful-presence status, no ineligible minimum
        # essential coverage, and the age-based premium requirement.
        pays_premium = person("pays_aca_premium", period)
        fstatus = person.tax_unit("filing_status", period)
        not_separate = fstatus != fstatus.possible_values.SEPARATE
        within_band = (magi_fraction >= p.fpl_floor) & (magi_fraction <= p.fpl_limit)
        return pays_premium & not_separate & within_band
