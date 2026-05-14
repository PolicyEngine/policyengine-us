from policyengine_us.model_api import *


class total_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "total self-employment income"
    unit = USD
    documentation = (
        "Total non-farm self-employment income, including both SSTB and "
        "non-SSTB Schedule C income."
    )
    definition_period = YEAR
    adds = ["self_employment_income", "sstb_self_employment_income"]
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#a"
    uprating = "calibration.gov.irs.soi.self_employment_income"
