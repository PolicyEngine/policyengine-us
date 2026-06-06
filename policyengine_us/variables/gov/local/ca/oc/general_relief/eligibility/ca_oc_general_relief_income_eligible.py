from policyengine_us.model_api import *


class ca_oc_general_relief_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Orange County General Relief income requirements"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Benefits_Services.pdf#page=01"

    def formula(spm_unit, period, parameters):
        # Financial eligibility exists when net countable income is below the
        # maximum aid payment. Sec 80.2.d determines financial eligibility by
        # subtracting net income -- computed per Sec 70.2 (income and deductions)
        # and Sec 70.3 (deemed and pooled income) -- from the GR MAP.
        countable_income = spm_unit("ca_oc_general_relief_countable_income", period)
        max_aid_payment = spm_unit("ca_oc_general_relief_max_aid_payment", period)
        return countable_income < max_aid_payment
