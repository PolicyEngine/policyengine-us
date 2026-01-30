from policyengine_us.model_api import *


class ri_works_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Rhode Island Works"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15",
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
    )
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("ri_works_countable_income", period)
        payment_standard = spm_unit("ri_works_payment_standard", period)
        return countable_income < payment_standard
