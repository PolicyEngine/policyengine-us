from policyengine_us.model_api import *


class ut_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah subtractions"
    unit = USD
    documentation = "Form TC-40, line 8"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323",
        "https://www.law.cornell.edu/uscode/text/45/231m#a",
    )

    adds = [
        "us_govt_interest",
        # 45 U.S.C. 231m(a): railroad retirement benefits in federal AGI.
        "taxable_railroad_benefits",
        "ut_other_subtractions",
    ]
