from openfisca_us.model_api import *


class medicaid_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Medicaid income"
    documentation = (
        "Modified adjusted gross income for calculating Medicaid eligibility."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#e_14_G",  # Medicaid law pointing to IRC
        "https://www.law.cornell.edu/uscode/text/26/36B#d_2",  # IRC defining income
    )

    def formula(spm_unit, period, parameters):
        # Medicaid law directs to use MAGI for individuals and 'household income' for families > 1 person.
        # 'Household income' is itself defined as the sum of MAGI for all individuals required to file taxes.
        person = spm_unit.members
        is_tax_unit_head = person("is_tax_unit_head", period)
        filer_medicaid_magi = is_tax_unit_head * person.tax_unit(
            "tax_unit_medicaid_magi", period
        )
        return spm_unit.sum(filer_medicaid_magi)
