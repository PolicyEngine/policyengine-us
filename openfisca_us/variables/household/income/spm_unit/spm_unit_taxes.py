from openfisca_us.model_api import *


class spm_unit_taxes(Variable):
    value_type = float
    entity = SPMUnit
    label = "Taxes"
    definition_period = YEAR
    unit = USD

    formula = sum_of_variables(
        [
            "spm_unit_payroll_tax",
            "spm_unit_self_employment_tax",
            "spm_unit_federal_tax",
            "spm_unit_state_tax",
            "flat_tax",
        ]
    )
