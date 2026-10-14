from policyengine_us.model_api import *


class military_retirement_pay(Variable):
    value_type = float
    entity = Person
    label = "Military retirement pay"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Retirement pay received by former members of the uniformed services "
        "of the United States. Included in federal gross income under 26 U.S.C. § 61(a)(10)."
    )
    reference = (
        "https://militarypay.defense.gov/Pay/Retirement/",
        "https://www.irs.gov/publications/p525",
    )
    uprating = "calibration.gov.irs.soi.taxable_pension_income"
