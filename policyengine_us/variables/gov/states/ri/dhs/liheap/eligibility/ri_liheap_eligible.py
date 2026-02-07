from policyengine_us.model_api import *


class ri_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Rhode Island LIHEAP"
    definition_period = YEAR
    reference = "https://dhs.ri.gov/programs-and-services/energy-assistance-programs-heating/low-income-home-energy-assistance-program"
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        return spm_unit("ri_liheap_income_eligible", period)
