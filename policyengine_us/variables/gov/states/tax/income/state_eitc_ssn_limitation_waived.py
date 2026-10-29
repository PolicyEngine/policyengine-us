from policyengine_us.model_api import *


class state_eitc_ssn_limitation_waived(Variable):
    value_type = bool
    entity = TaxUnit
    label = "State EITC waives the Social Security number limitation"
    documentation = "Whether the state's earned income credit computes the federal credit without the IRC 32(m) Social Security number limitation. The branch federal_eitc_tax_unit (tools/state_eitc_helpers.py) creates takes this as eitc_ssn_limitation_waived, so every state credit that reads the branch sees the same tax units waived."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#m"

    def formula(tax_unit, period, parameters):
        return tax_unit("md_eitc_ssn_limitation_waived", period) | tax_unit(
            "me_eitc_ssn_limitation_waived", period
        )
