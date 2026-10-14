from policyengine_us.model_api import *


class military_retirement_pay_survivors(Variable):
    value_type = float
    entity = Person
    label = "Military retirement income paid to surviving spouses"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Survivor annuity payments received by surviving spouses or other designated "
        "beneficiaries under a United States uniformed services retirement plan (such as "
        "the Survivor Benefit Plan or Retired Serviceman's Family Protection Plan). "
        "Included in federal gross income under 26 U.S.C. § 61(a)(10) and § 72."
    )
    reference = (
        "https://militarypay.defense.gov/Benefits/Survivor-Benefit-Program/",
        "https://www.irs.gov/publications/p525",
        "https://www.irs.gov/publications/p575",
    )
    uprating = "calibration.gov.irs.soi.taxable_pension_income"
