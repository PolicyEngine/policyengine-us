from policyengine_us.model_api import *


class ga_low_income_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia low income credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download",
        # 2025 IT-511, Line 17: only if "you are not claimed or eligible to be
        # claimed as a dependent on another taxpayer's Federal or Georgia
        # income tax return".
        "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download#page=17",
        "https://dor.georgia.gov/low-income-tax-credit",
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # We follow the legal code, which says (in addition to head and spouse):
        # "multiplied by the number of dependents which the taxpayer is entitled to claim."
        # The tax form excludes adult dependents:
        # "Exemptions are self, spouse and natural or legally adopted children"
        # Georgia counts its own exemptions (O.C.G.A. 48-7A-3 deems each joint
        # spouse a dependent), not the federal count, which leaves out a
        # filer who can be claimed as a dependent.
        exemptions = tax_unit("tax_unit_size", period)
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
        # O.C.G.A. 48-7A-3 allows the credit only to a taxpayer who is not
        # claimed or eligible to be claimed as a dependent. The return-level
        # worksheet counts self, spouse and children, so either spouse being
        # claimable bars the joint return.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return total_exemptions * amount_per_exemption * ~filer_is_dependent
