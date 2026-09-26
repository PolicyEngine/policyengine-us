from policyengine_us.model_api import *


class co_low_income_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado Low-income Child Care Expenses Credit"
    # C.R.S. 39-22-119.5(3)(a) eligibility conditions and statutory window.
    # PolicyEngine models the availability window, the $25,000 AGI limit,
    # the insufficient-federal-liability condition (no federal CDCC allowed
    # after the section 26 liability limitation), and the IRC 21(e)(2)
    # joint-return requirement. The provider identification / due-diligence
    # requirements (provider name, address, and TIN under (5)(a)-(b)) and
    # the dependent identification requirements under (5)(c) are
    # administrative inputs PolicyEngine does not model and are assumed
    # satisfied. The
    # dependent-under-age-13 condition (3)(a)(III) is applied in
    # co_low_income_cdcc.
    reference = (
        "https://law.justia.com/codes/colorado/title-39/specific-taxes/income-tax/article-22/part-1/section-39-22-119-5/",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=46",
        # C.R.S. 39-22-119.5(3)(a) (window narrowed to before 2026 by HB24-1134)
        "https://leg.colorado.gov/sites/default/files/2024a_1134_signed.pdf#page=3",
    )
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits
        # C.R.S. 39-22-119.5(3)(a): the credit is available only for income tax
        # years within the statutory window (2014-2016 and 2018-2025; repealed
        # for tax years beginning on or after January 1, 2026 by HB24-1134).
        available = p.cdcc.low_income.available
        # C.R.S. 39-22-119.5(3)(a)(II): the filer has insufficient tax liability
        # to claim any credit under section 39-22-119. The credit backstops
        # filers whose federal CDCC is zeroed out by their income tax
        # liability; a separate filer excluded from the federal credit by the
        # IRC 21(e)(2) joint-return requirement remains ineligible.
        no_fed_cdcc = tax_unit("capped_cdcc", period) <= 0
        filing_status_eligible = tax_unit("cdcc_filing_status_eligible", period)
        # C.R.S. 39-22-119.5(3)(a)(I): federal AGI at or below $25,000.
        fed_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = fed_agi <= p.cdcc.low_income.federal_agi_threshold
        return available & no_fed_cdcc & agi_eligible & filing_status_eligible
