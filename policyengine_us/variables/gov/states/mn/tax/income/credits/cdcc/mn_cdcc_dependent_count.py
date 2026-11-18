from policyengine_us.model_api import *


class mn_cdcc_dependent_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child and dependent care expense credit dependent count"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf",
        "https://www.revisor.mn.gov/statutes/cite/290.067",
        "https://www.law.cornell.edu/uscode/text/26/21#b_1",
    )
    defined_for = "mn_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        person = tax_unit.members
        # calculate number of qualifying dependents
        # ... children
        age = person("age", period)
        qualifies_by_age = age < p.child_age
        # ... disability: a dependent, or the taxpayer's spouse, who cannot
        # care for themselves (IRC 21(b)(1)(B)-(C)). On a joint return either
        # spouse can be the other's qualifying spouse, and, as in the federal
        # count_cdcc_eligible, the couple counts at most one such spouse.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disabled = person("is_incapable_of_self_care", period)
        qualifies_by_disability = ~head_or_spouse & disabled
        has_spouse = tax_unit.any(person("is_tax_unit_spouse", period))
        qualifying_spouse = has_spouse & tax_unit.any(
            head_or_spouse & disabled & ~qualifies_by_age
        )
        return tax_unit.sum(qualifies_by_age | qualifies_by_disability) + (
            qualifying_spouse
        )
