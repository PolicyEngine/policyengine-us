from policyengine_us.model_api import *


class ar_can_file_separate_on_same_return(Variable):
    value_type = bool
    entity = Person
    label = "Whether married couples in Arkansas can file separately on the same return"
    definition_period = YEAR
    defined_for = StateCode.AR
    default_value = False

    def formula(person, period, parameters):
        state_filing_status = person.tax_unit("state_filing_status_if_married_filing_separately_on_same_return", period)
        return state_filing_status == state_filing_status.possible_values.SEPARATE
