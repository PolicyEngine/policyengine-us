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
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # The instructions say to count only self, spouse and children.
        # Georgia lawmakers count all entitled dependents in O.C.G.A.
        # 48-7A-3(a), and expressly count both spouses on a joint return.
        # Either eligible spouse can claim for both spouse units. IRC
        # 152(b)(1) bars child units when either filer is a dependent outside
        # the filing exception. The statutory claimed-or-otherwise-eligible
        # disjunction remains open; the model keeps the claimed-or-claimable
        # exclusion for the taxpayer's own eligibility.
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
