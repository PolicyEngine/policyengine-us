from policyengine_us.model_api import *


class md_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA gross unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    adds = "gov.states.md.tanf.income.sources.unearned"
