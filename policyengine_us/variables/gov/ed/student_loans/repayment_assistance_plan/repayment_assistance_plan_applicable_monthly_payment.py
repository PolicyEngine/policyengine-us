from policyengine_us.model_api import *


class repayment_assistance_plan_applicable_monthly_payment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Repayment Assistance Plan applicable monthly payment"
    documentation = (
        "Base payment divided by 12, minus the dependent reduction, and no "
        "less than the minimum payment. Spousal proration and the final-payment "
        "cap apply per borrower in repayment_assistance_plan_payment."
    )
    unit = USD
    definition_period = MONTH
    # NOTE: A person-level defined_for applies when any tax unit member is an
    # eligible borrower.
    defined_for = "repayment_assistance_plan_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title20-section1087e&num=0&edition=prelim",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=274",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(3)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(5)",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.ed.student_loans.repayment_assistance_plan
        # NOTE: Reading the annual base payment for a month divides it by 12.
        monthly_base_payment = tax_unit(
            "repayment_assistance_plan_base_payment", period
        )
        dependents = tax_unit("tax_unit_dependents", period.this_year)
        reduced_payment = monthly_base_payment - p.dependent_reduction * dependents
        return max_(reduced_payment, p.minimum_payment)
