from policyengine_us.model_api import *


class il_aabd_utility_allowance_person(Variable):
    value_type = float
    entity = Person
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) utility allowance per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.259",
    )

    def formula(person, period, parameters):
        utility_allowance = person.spm_unit(
            "il_aabd_utility_allowance", period
        )
        size = person.spm_unit("spm_unit_size", period)
        # Prorate the total utility allowance across all household members
        return utility_allowance / size
