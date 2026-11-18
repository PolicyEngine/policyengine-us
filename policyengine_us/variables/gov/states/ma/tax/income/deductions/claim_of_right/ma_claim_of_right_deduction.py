from policyengine_us.model_api import *


class ma_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts claim of right deduction"
    unit = USD
    documentation = (
        "Massachusetts Part B deduction for repaying income included in "
        "Massachusetts taxable income in an earlier year under a claim of "
        "right (Schedule Y, line 14). It applies to repayments of any amount, "
        "whichever federal method applies."
    )
    definition_period = YEAR
    reference = (
        # M.G.L. c. 62, s. 3(B)(a)(14)
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section3",
        # DOR explicitly allows the deduction without regard to the amount paid.
        "https://www.mass.gov/info-details/differences-between-ma-and-federal-tax-law-for-personal-income",
        "https://www.mass.gov/technical-information-release/tir-06-4-deduction-for-income-upon-which-taxes-have-been-paid-under-a-claim-of-right",
        # 2025 Form 1 instructions, Schedule Y line 14
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2025/ma-dor-2025-inc-form-1-inst.pdf#page=21",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2025/ma-dor-2025-inc-sch-y.pdf",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        repayment = person("claim_of_right_repayment", period)
        excluded = person("ma_claim_of_right_repayment_excluded_from_income", period)
        # Dependents' repayments belong on their own returns.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(max_(repayment - excluded, 0) * head_or_spouse)
