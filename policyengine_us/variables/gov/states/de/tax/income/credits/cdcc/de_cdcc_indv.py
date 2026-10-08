from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.de.tax.income.de_combined_separate_credits import (
    de_combined_separate_credit_choices,
)


class de_cdcc_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware CDCC per person for combined separate filing"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=10"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # PIT-RES Line 31: "the credit may only be applied against
        # the tax imposed on the spouse with the lower taxable
        # income reported on Line 23."  Locked to the lower-income
        # spouse's column under combined separate filing.
        # With equal taxable incomes either spouse has the lower income; the
        # column is then chosen with the other column credits to minimise tax
        # (see de_combined_separate_credit_choices).
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        _, cdcc_head, _ = de_combined_separate_credit_choices(
            person.tax_unit, period, parameters
        )
        takes = (is_head & cdcc_head) | (is_spouse & ~cdcc_head)
        return takes * person.tax_unit("de_cdcc", period)
