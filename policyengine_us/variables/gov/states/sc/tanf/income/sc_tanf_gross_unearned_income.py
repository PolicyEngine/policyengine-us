from policyengine_us.model_api import *


class sc_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "South Carolina TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://dss.sc.gov/media/ojqddxsk/tanf-policy-manual-volume-65.pdf#page=100"  # Section 7.1
    adds = "gov.states.sc.tanf.income.unearned"
