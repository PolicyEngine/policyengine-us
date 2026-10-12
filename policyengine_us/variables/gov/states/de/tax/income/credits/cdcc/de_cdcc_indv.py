from policyengine_us.model_api import *


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
        # Tie-break: when taxable incomes are equal, head is treated
        # as the higher-income spouse, so CDCC routes to spouse.
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)

        person_taxable = person("de_taxable_income_indv", period)
        head_taxable = person.tax_unit.sum(is_head * person_taxable)
        spouse_taxable = person.tax_unit.sum(is_spouse * person_taxable)
        head_higher = head_taxable >= spouse_taxable

        is_lower_income = (is_head & ~head_higher) | (is_spouse & head_higher)
        return is_lower_income * person.tax_unit("de_cdcc", period)
