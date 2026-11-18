from policyengine_us.model_api import *


class federal_student_loan_graduate_share(Variable):
    value_type = float
    entity = Person
    label = "Federal student loan graduate share"
    documentation = (
        "Share of the original principal of the loans in "
        "federal_student_loan_balance that the person did not receive for "
        "undergraduate study, such as loans for graduate or professional "
        "study. Zero means every loan was for undergraduate study."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(1)(ii)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(f)(1)(iii)",
    )
