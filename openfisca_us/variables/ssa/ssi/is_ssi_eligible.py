from openfisca_us.model_api import *


class is_ssi_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Eligibility for Supplemental Security Income"
    label = "SSI eligibility"

    def formula(person, period, parameters):
        return (
            spm_unit.has_valid_ssi_income
            and spm_unit.has_valid_ssi_income_credits
            and spm_unit.has_valid_ssi_income_and_credits
        )
