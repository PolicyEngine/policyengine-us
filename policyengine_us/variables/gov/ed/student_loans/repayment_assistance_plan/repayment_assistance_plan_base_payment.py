from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.student_loans.student_loan_borrower_income_helpers import (
    repayment_assistance_plan_annual_base_payment,
)


class repayment_assistance_plan_base_payment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Repayment Assistance Plan base payment"
    documentation = (
        "Annual base payment from the bracket rate on the whole adjusted "
        "gross income of the most recent return "
        "(income_driven_repayment_adjusted_gross_income), or the low-income "
        "amount when that income is not more than the rate scale's first "
        "finite threshold. This is the base payment of the head and spouse "
        "of the tax unit. A borrower claimed as a tax dependent has a base "
        "payment on their own income, computed in "
        "repayment_assistance_plan_payment."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=274",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(2)",
    )

    def formula(tax_unit, period, parameters):
        agi = tax_unit("income_driven_repayment_adjusted_gross_income", period)
        return repayment_assistance_plan_annual_base_payment(agi, period, parameters)
