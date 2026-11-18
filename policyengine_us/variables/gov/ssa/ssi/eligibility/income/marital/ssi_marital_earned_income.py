from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_income,
)


class ssi_marital_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Combined SSI earned income of the two spouses"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1802#p-416.1802(b)(1)",
        "https://www.ecfr.gov/current/title-20/section-416.414#p-416.414(a)(1)",
        "https://www.ecfr.gov/current/title-20/section-416.414#p-416.414(b)(3)",
    )

    def formula(person, period, parameters):
        # 416.1802(b)(1): with an eligible spouse 'we will count your combined
        # income'. Combine the two spouses, not every member of the unit.
        # 416.414(b)(3) counts 'each individual's own countable income' in a
        # month one spouse spends throughout in a medical treatment facility,
        # from the start of the month to its end (416.414(a)(1)), so each
        # month follows its own status.
        return _ssi_couple_income(person, period, "ssi_earned_income")
