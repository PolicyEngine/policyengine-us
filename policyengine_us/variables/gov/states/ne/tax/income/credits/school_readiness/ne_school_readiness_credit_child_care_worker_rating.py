from policyengine_us.model_api import *


class ne_school_readiness_credit_child_care_worker_rating(Variable):
    value_type = int
    entity = Person
    label = "Level of child care worker for the Nebraska school readiness refundable tax credit"
    definition_period = YEAR
    defined_for = StateCode.NE
    reference = "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2024/f_Individual_Income_Tax_Booklet.pdf#page=2"
