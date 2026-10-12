from policyengine_us.model_api import *


class co_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    # Colorado state flat premium wrap on top of the federal ACA premium tax
    # credit, administered by Connect for Health Colorado and funded by the
    # Health Insurance Affordability Enterprise. The monthly amount is a flat
    # build-up: a first-member amount plus an additional-member amount for each
    # further member, annualized as twelve times the monthly amount and capped
    # at the remaining premium after the federal credit.
    #
    # Approximations:
    # - The enrolled-plan premium is approximated by the benchmark SLCSP (the
    #   residual cap is SLCSP minus the federal PTC, floored at zero).
    # - The count of members with a remaining premium is approximated by the
    #   count of members eligible for the federal ACA PTC. Regulation 4-2-78
    #   Section 5.B instead counts QHP members "subject to a premium" with a
    #   per-member lesser-of test; is_aca_ptc_eligible embeds PTC income, MFS,
    #   and coverage screens, so a CHP+ child drops from the count and an MFS
    #   parent zeroes the unit, though the regulation applies no filing-status
    #   test. The per-member wrap is approximated as a pooled unit-level amount.
    # - Full-year enrollment is assumed via the times-twelve annualization.
    #
    # Colorado Premium Assistance is paid upfront and is not a tax credit, so no
    # reconciliation or tax-return interaction is modeled.
    #
    # Not modeled: a tax unit that mixes OmniSalud and Colorado Premium
    # Assistance members. OmniSalud (co_omnisalud) and Colorado Premium
    # Assistance are valued independently, so a mixed unit may be double-counted
    # relative to enrollment rules; this compounds the pre-existing OmniSalud
    # valuation approximation.
    reference = (
        # Amended Regulation 4-2-78 (3 CCR 702-4), Section 5.B (first-member
        # Section 5.B.1, additional-member Section 5.B.2, under-21 $0-premium
        # rule). Adopted via the DOI notice below (which returns HTTP 403 to
        # non-browser user agents).
        "https://drive.google.com/file/d/1GkpvQTauvS4hr97_CSfkSEQCnoYjqrJI/view",
        "https://doi.colorado.gov/announcements/notice-of-adoption-amended-regulation-4-2-78-concerning-health-insurance",
        # Enrolled HB25B-1006, Section 10-16-1207(5) (rule authority) and
        # Section 10-16-1205(1)(b)(II) (payment authority).
        "https://content.leg.colorado.gov/sites/default/files/documents/2025B/bills/2025b_1006_enr.pdf",
        "https://connectforhealthco.com/new-customers/tips-for-choosing-a-plan/colorado-premium-assistance/",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.doi.premium_assistance
        # Count members with a remaining premium, approximated by members
        # eligible for the federal ACA PTC. Regulation 4-2-78 Section 5.B has no
        # member cap; the under-21 $0-premium exclusion is already applied
        # through pays_aca_premium inside is_aca_ptc_eligible.
        n = add(tax_unit, period, ["is_aca_ptc_eligible"])
        flat_monthly = where(
            n > 0,
            p.amount.first_member + p.amount.additional_member * (n - 1),
            0,
        )
        # slcsp is a MONTH-period variable; core sums the 12 months when called
        # from this YEAR formula. Approximates the enrolled-plan premium.
        slcsp_annual = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        residual = max_(0, slcsp_annual - aca_ptc)
        annual = min_(MONTHS_IN_YEAR * flat_monthly, residual)
        eligible = tax_unit("co_premium_assistance_eligible", period)
        return where(eligible, annual, 0)
