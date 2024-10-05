from policyengine_us.model_api import *


class hi_dependent_care_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii Dependent Care Benefits"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=40"
        "https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=1"
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.hi.tax.income.credits.cdcc.dependent_care_benefits
        p_irs = parameters(
            period
        ).gov.irs.gross_income.dependent_care_assistance_programs
        # Schedule X PART II:
        # line 2:
        dcb_amount = add(
            tax_unit, period, ["dependent_care_employer_benefits"]
        )
        # line 3, 4 are ignored, so line 5 = line 2
        # line 6:
        qualified_expense_amount = tax_unit(
            "tax_unit_childcare_expenses", period
        )
        # line 7 = min(line 5, line 6) = min(line 2, line 6):
        capped_expenses = min_(dcb_amount, qualified_expense_amount)
        # line 8 & line 9:
        # married persons must file a joint return to claim the credit
        # if single, the min will be his/her income
        min_head_spouse_earned = tax_unit(
            "hi_cdcc_min_head_spouse_earned", period
        )
        # line 10 = min(line 7, line 8, line 9):
        earned_income_cap = min_(capped_expenses, min_head_spouse_earned)
        # line 11:
        filing_status = tax_unit("filing_status", period)
        dcb_baseline = p_irs.reduction_amount[filing_status]
        # line 12 is ignored, since we do not consider sole proprietorship/partnership
        # line 13 is ignored, since it requires line 12
        # line 14:
        deductible_benefit = min_(earned_income_cap, dcb_baseline)
        # line 15 excluded_benefit = 0 since we ignore line 12
        # line 16 Taxable Benefit is ignored, since we never use it
        # line 17:
        expenses_amount = p.expense_floor.calc(
            tax_unit("count_cdcc_eligible", period)
        )
        # line 18 = line 14 + line 15 = line 14
        # line 19 = line 17 - line 18 = line 17 - line 14
        net_expenses = max_(0, expenses_amount - deductible_benefit)
        # line 20 = line 21 (d) = line 6
        # return line 22 = min(line 19, line 20) since we complete section B
        return min_(net_expenses, qualified_expense_amount)
