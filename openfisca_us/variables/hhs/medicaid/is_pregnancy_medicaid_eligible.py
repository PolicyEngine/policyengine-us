from openfisca_us.model_api import *


class is_pregnancy_medicaid_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Eligible for Pregnancy-Related Medicaid"
    documentation = "Whether the woman and unborn child/children qualify for Pregnancy Medicaid."
    # TODO: add reference.

    def formula(person, period, parameters):
        income = person.spm_unit("medicaid_gross_income", period)
        fpg = person.spm_unit("spm_unit_fpg", period)
        # TODO: Change to is_medicaid_eligible.
        fpg_income_threshold = person("medicaid_income_threshold", period)
        # TODO: add hhs/medicaid/pregnancy/income_limit.yaml and reference.
        # fpg_2_income_threshold = person(2.13, period)
        pregnant = person("is_pregnant", period)
        # TODO: Confirm newborns are eligible.
        child_0 = person("age", period) == 0
        income_share_of_fpg = income / fpg
        return (
            (income_share_of_fpg > fpg_income_threshold)
            & (income_share_of_fpg <= 2.13)
            & (pregnant | child_0)
        )
