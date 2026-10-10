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
        # O.C.G.A. 48-7A-3(a) as amended by HB 1069 (2010), section 5, printed
        # page 1172.
        "https://dlg.usg.edu/record/dlg_ggpd_y-ga-bl407-b2010-bv-p1-bbk-p1-belec-p-btext",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # We follow the legal code, which says (in addition to head and spouse):
        # "multiplied by the number of dependents which the taxpayer is entitled to claim."
        # The tax form excludes adult dependents:
        # "Exemptions are self, spouse and natural or legally adopted children"
        # O.C.G.A. 48-7A-3(a): "each resident taxpayer ... who is not claimed
        # or is not otherwise eligible to be claimed as a dependent" may claim
        # the credit, and "A husband and wife filing a joint return shall each
        # be deemed a dependent for purposes of such joint return". So Georgia
        # counts its own units rather than federal exemptions, and a joint
        # return keeps both spouses' units while either spouse can claim. A
        # return on which a filer can be claimed has no dependents (Georgia
        # follows the federal rules, IRC 152(b)(1)).
        size = tax_unit("tax_unit_size", period)
        dependents = tax_unit("tax_unit_dependents", period)
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        exemptions = where(filer_is_dependent, size - dependents, size)
        eligible = tax_unit("head_spouse_count_not_dependent_elsewhere", period) > 0
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
