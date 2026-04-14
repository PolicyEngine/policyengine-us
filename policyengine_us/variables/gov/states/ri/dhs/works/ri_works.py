from policyengine_us.model_api import *


class ri_works(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island Works benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
        "https://dhs.ri.gov/programs-and-services/ri-works-program",
    )
    defined_for = "ri_works_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ri_works_payment_standard", period)
        countable_income = spm_unit("ri_works_countable_income", period)
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
