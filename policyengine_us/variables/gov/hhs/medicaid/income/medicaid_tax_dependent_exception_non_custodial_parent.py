from policyengine_us.model_api import *


class medicaid_tax_dependent_exception_non_custodial_parent(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid MAGI tax-dependent exception for a child claimed by a non-custodial parent"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2_iii"

    def formula(person, period, parameters):
        # PolicyEngine US does not currently carry parent-custody identifiers, so
        # this exception cannot yet be distinguished from other dependent cases.
        return False
