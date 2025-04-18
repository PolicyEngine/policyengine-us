from policyengine_us.model_api import *


class ne_school_readiness_credit_eligible_worker(Variable):
    value_type = bool
    entity = Person
    label = "Eligible worker for the Nebraska school readiness refundable tax credit"
    definition_period = YEAR
    reference = "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2024/f_Individual_Income_Tax_Booklet.pdf#page=2"
    defined_for = StateCode.NE
    default_value = False
