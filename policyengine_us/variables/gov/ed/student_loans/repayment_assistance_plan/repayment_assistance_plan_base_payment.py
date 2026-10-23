from policyengine_us.model_api import *


class repayment_assistance_plan_base_payment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Repayment Assistance Plan base payment"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=274",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(2)",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.ed.student_loans.repayment_assistance_plan.base_payment
        agi = tax_unit("adjusted_gross_income", period)
        # The low-income limit is the first finite threshold of the rate scale.
        low_income = agi <= p.rate.thresholds[1]
        income_based_payment = p.rate.calc(agi, right=True) * agi
        return where(low_income, p.low_income_amount, income_based_payment)
