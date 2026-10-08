from policyengine_us.model_api import *


class hi_mortgage_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii home mortgage interest deduction"
    unit = USD
    documentation = (
        "Home mortgage interest Hawaii allows on Worksheet A-3. Hawaii makes "
        "IRC 163(h)(3)(F) inoperative, so the pre-TCJA home acquisition and "
        "home equity debt limits apply regardless of when the debt arose."
    )
    reference = (
        "https://data.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0002_0004.htm",
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/HB2329_CD1_.pdf#page=20",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=17",
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=11",
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized.interest
        filing_status = tax_unit("filing_status", period)
        # 2017 Publication 936, Table 1. Grandfathered debt from before
        # October 14, 1987 (line 1) is not modeled, so every balance is home
        # acquisition debt (line 2).
        debt = add(
            tax_unit,
            period,
            ["first_home_mortgage_balance", "second_home_mortgage_balance"],
        )
        # Line 6.
        acquisition_debt = min_(debt, p.home_acquisition_debt_limit[filing_status])
        # Line 7. Debt over the home acquisition debt limit may qualify as home
        # equity debt. The fair market value limit on home equity debt is not
        # modeled.
        home_equity_debt = min_(
            debt - acquisition_debt, p.home_equity_debt_limit[filing_status]
        )
        # Line 8.
        qualified_loan_limit = acquisition_debt + home_equity_debt
        # Line 11. Without a reported balance, the interest is treated as
        # within the limits, as in the federal calculation.
        deductible_share = np.divide(
            qualified_loan_limit,
            debt,
            out=np.ones_like(debt),
            where=debt > 0,
        )
        # Line 10 uses total interest paid, before the federal debt cap.
        # This also preserves the canonical filer input's priority over
        # the deprecated first/second-home interest inputs.
        gross_interest = tax_unit("home_mortgage_interest_tax_unit", period)
        legacy_interest = tax_unit_non_dep_add(tax_unit, period, ["mortgage_interest"])
        supplied_deduction = tax_unit_non_dep_add(
            tax_unit, period, ["deductible_mortgage_interest"]
        )
        # Legacy gross interest can be supplied directly or reconstructed
        # from deductible and non-deductible components. Deductible interest
        # alone has already been limited and must not receive a second cap.
        has_gross_interest = (gross_interest > 0) | (
            legacy_interest > supplied_deduction
        )
        interest = where(gross_interest > 0, gross_interest, legacy_interest)
        # Line 12. Retain the supplied-deductible fallback when gross interest
        # is unavailable, even if a mortgage balance has been reported.
        return where(
            has_gross_interest, interest * deductible_share, supplied_deduction
        )
