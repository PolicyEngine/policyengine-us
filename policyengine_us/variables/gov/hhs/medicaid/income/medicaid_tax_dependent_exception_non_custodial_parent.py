from policyengine_us.model_api import *


class medicaid_tax_dependent_exception_non_custodial_parent(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid MAGI tax-dependent exception for a child claimed by a non-custodial parent"
    documentation = (
        "Direct input for the Medicaid MAGI exception that applies when a "
        "child is claimed by a non-custodial parent. PolicyEngine does not "
        "currently link a child to a claiming parent outside the tax unit."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2_iii"
