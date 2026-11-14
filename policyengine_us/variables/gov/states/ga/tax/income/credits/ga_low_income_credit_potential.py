from policyengine_us.model_api import *


class ga_low_income_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia low income credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download",
        # 2025 IT-511, Line 17 excludes claimed and claimable filers.
        "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download#page=17",
        "https://dor.georgia.gov/low-income-tax-credit",
        # O.C.G.A. 48-7A-3(a) as amended by HB 1069 (2010), section 5, printed
        # page 1172.
        "https://dlg.usg.edu/record/dlg_ggpd_y-ga-bl407-b2010-bv-p1-bbk-p1-belec-p-btext",
        # IRC 152(b)(1).
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partV-sec152.htm",
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # Georgia lawmakers count both spouses under O.C.G.A. 48-7A-3(a)(1).
        # They set the amount per credit unit in subsection (b).
        # Either eligible spouse can claim for both spouse units. Filers
        # who qualify as dependents outside the filing exception cannot
        # count child units under IRC 152(b)(1). Lawmakers extended the exclusion
        # to claimable filers in 2010. Read the conditions as one exclusion
        # so the added clause reaches unclaimed but eligible dependents.
        size = tax_unit("tax_unit_size", period)
        dependents = tax_unit("tax_unit_dependents", period)
        filer_is_dependent = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        exemptions = where(filer_is_dependent, size - dependents, size)
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        excluded = person("claimed_as_dependent_on_another_return", period) | person(
            "claimable_as_dependent_on_another_return", period
        )
        eligible = tax_unit.any(filer & ~excluded)
        p = parameters(period).gov.states.ga.tax.income.credits.low_income
        # age threshold
        age_threshold = p.supplement_age_eligibility
        aged_head = (tax_unit("age_head", period) >= age_threshold).astype(
            int
        )  # if so, return 1, otherwise return 0
        aged_spouse = (tax_unit("age_spouse", period) >= age_threshold).astype(
            int
        )  # if so, return 1, otherwise return 0
        aged_count = aged_head + aged_spouse
        total_exemptions = aged_count + exemptions
        federal_agi = tax_unit("adjusted_gross_income", period)
        amount_per_exemption = p.amount.calc(federal_agi)
        return total_exemptions * amount_per_exemption * eligible
