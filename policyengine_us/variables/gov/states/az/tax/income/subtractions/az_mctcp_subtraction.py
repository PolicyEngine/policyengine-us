from policyengine_us.model_api import *


class az_mctcp_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Middle Class Tax Cuts Package subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_MCTCP_0.pdf",
        "https://azgovernor.gov/office-arizona-governor/executive-order/2025-15",
        "https://azdor.gov/news-center/ador-outlines-executive-order-and-2025-tax-year-income-tax-forms",
    )

    def formula(tax_unit, period, parameters):
        # Per Governor Hobbs' Executive Order 2025-15 and the ADOR MCTCP
        # worksheet for 2025 Form 140, Arizona conforms to four OBBBA Schedule
        # 1-A deductions as Other Subtractions. PE-US already computes the
        # federal amounts; this variable propagates them to AZ subtractions.
        return (
            tax_unit("additional_senior_deduction", period)
            + tax_unit("tip_income_deduction", period)
            + tax_unit("overtime_income_deduction", period)
            + tax_unit("auto_loan_interest_deduction", period)
        )
