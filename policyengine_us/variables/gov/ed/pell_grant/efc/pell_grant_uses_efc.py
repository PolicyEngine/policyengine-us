from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.pell_grant.pell_grant_calculation_method import PellGrantCalculationMethod


class pell_grant_uses_efc(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Pell Grant uses the expected family contribution"

    def formula(person, period, parameters):
        method = person.tax_unit("pell_grant_calculation_method", period)
        return method == PellGrantCalculationMethod.EFC
