from openfisca_us.model_api import *


class is_ctc_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for CTC (child)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

    def formula(person, period, parameters):
        ctc = parameters(period).irs.credits.child_tax_credit
        age = person("age", period)
        return age <= ctc.eligibility.max_age
