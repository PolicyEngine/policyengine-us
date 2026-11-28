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
        "A person is a New Jersey Health Plan Savings enrollee when they pay an "
        "ACA marketplace premium, are in the federal premium tax credit tax "
        "family (an interpretation: Treasury's 1332 addendum describes NJHPS "
        "as for enrollees 'otherwise eligible for the Advanced Premium Tax "
        "Credit', and no current New Jersey rule found addresses someone "
        "another taxpayer can claim), do not file a separate return, "
        "and household "
        "income (ACA MAGI per 26 U.S.C. 36B(d)(2)) falls within the 138-600% "
        "FPL NJHPS band. This deliberately does NOT reuse is_aca_ptc_eligible: "
        "that variable embeds the federal 400% FPL income cliff (the PY2026 "
        "baseline sets the ptc_income_eligibility 400% threshold to false, so "
        "is_aca_ptc_eligible is False and aca_ptc is 0 above 400% FPL), which "
        "would drop the 400-600% band that NJHPS covers and that is the single "
        "most PY2026-relevant band because federal APTC is $0 there. Instead "
        "the gate reproduces the Marketplace enrollment test via "
        "pays_aca_premium (TIN, lawful-presence/immigration status, no "
        "ineligible minimum essential coverage, the age-based premium test "
        "and, since policyengine-us #9506, the Medicaid coverage gap) plus "
        "the married-filing-separately exclusion, and substitutes NJHPS's own "
        "138-600% FPL income band for the federal 400% cliff. The coverage-gap "
        "exclusion carried by pays_aca_premium is non-binding here, because "
        "the NJHPS band starts at 138% FPL, above the federal PTC floor the "
        "gap sits under. This mirrors the enrollment-internals pattern used "
        "for the above-400% bands in New Mexico and Washington."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.dobi.njhps
        # DOBI's plan year 2026 schedule runs to "less than or equal to 600%
        # FPL" ($0 "Above 600% FPL"). Test the exact ratio, not the truncated
        # aca_magi_fraction: truncation maps 600.00%-600.99% to 6.00, which
        # would admit incomes above 600%. The 138% floor (">=") is unaffected
        # by truncation. Both are TaxUnit quantities read at the person level.
        # No New Jersey source found defines the poverty line. Published dollar
        # limits imply the guideline year, which aca_fpg matches: DOBI gave
        # $93,900 for one person in July 2026 (600% of the 2025 guideline), and
        # Get Covered NJ gives $95,760 during open enrollment for 2027 (600% of
        # the 2026 guideline). Get Covered NJ applies the limit to "tax
        # households" without defining the term or saying whether a filer who
        # can be claimed on another return counts. Leaving that filer out, as
        # aca_fpg does, is a modeling choice.
        magi = max_(person.tax_unit("aca_magi", period), 0)
        fpg = person.tax_unit("aca_fpg", period)
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it.
        exact_magi_frac = magi.astype(np.float64) / fpg
        # pays_aca_premium is the Person-level Marketplace enrollment test:
        # TIN, immigration/lawful-presence status, no ineligible minimum
        # essential coverage, the age-based premium requirement and, since
        # policyengine-us #9506, the Medicaid coverage gap. That last piece is
        # the only income component and it cannot bind here: it excludes
        # income under the federal PTC floor of 100% FPL, and within_band
        # already starts at the 138% FPL NJHPS floor.
        pays_premium = person("pays_aca_premium", period)
        # Interpretation: NJHPS goes to enrollees otherwise eligible for APTC
        # (Treasury 1332 addendum), so a person outside the federal tax family
        # (one who can be claimed on another return, or a dependent of a
        # return with such a filer) is not a member; 26 U.S.C. 36B(c)(1)(D)
        # is not one of the income tests NJHPS replaces.
        tax_family_member = person("is_aca_tax_family_member", period)
        fstatus = person.tax_unit("filing_status", period)
        not_separate = fstatus != fstatus.possible_values.SEPARATE
        within_band = (exact_magi_frac >= p.fpl_floor) & (
            exact_magi_frac <= p.fpl_limit
        )
        return pays_premium & tax_family_member & not_separate & within_band
