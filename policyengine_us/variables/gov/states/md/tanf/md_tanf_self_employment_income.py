from policyengine_us.model_api import *

# reference: "https://www.law.cornell.edu/uscode/text/26/1402#a"


class md_tanf_self_employment_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF self employment income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    adds = "gov.irs.tax.self_employment.taxable_self_employment_income"
