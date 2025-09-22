from policyengine_us.model_api import *


class mn_cdcc_dependent_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child and dependent care expense credit dependent count"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf"
    )
    defined_for = "mn_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        person = tax_unit.members
        # calculate number of qualifying dependents
        # ... children
        age = person("age", period)
        qualifies_by_age = age < p.child_age
        # ... disability
        non_head = ~person("is_tax_unit_head", period)
        disabled = person("is_incapable_of_self_care", period)
        qualifies_by_disability = non_head & disabled
        return tax_unit.sum(qualifies_by_age | qualifies_by_disability)
