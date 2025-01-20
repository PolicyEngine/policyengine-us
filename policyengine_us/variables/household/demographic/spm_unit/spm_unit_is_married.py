from policyengine_us.model_api import *


class spm_unit_is_married(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM unit is married"
    documentation = "Whether the adults in this SPM unit are married."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        # If any tax unit is a married filer, assume the family is.
        person = spm_unit.members
        filing_status = person.tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        person_is_married = is_in(
            person.tax_unit("filing_status", period),
            [
                filing_statuses.JOINT,
                filing_statuses.SEPARATE,
            ],
        )
        return spm_unit.any(person_is_married)
