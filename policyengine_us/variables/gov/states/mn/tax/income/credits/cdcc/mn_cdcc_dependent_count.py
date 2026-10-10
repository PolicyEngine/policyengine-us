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
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = "mn_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        person = tax_unit.members
        # Minn. Stat. 290.067 allows the credit for qualifying individuals
        # under IRC 21(b)(1).
        # ... children: Schedule M1CD counts "your dependent child who is
        # younger than 13" (IRC 21(b)(1)(A)). Under IRC 152(b)(1) a return on
        # which the filer, or on a joint return either spouse, can be claimed
        # as a dependent has no dependents.
        age = person("age", period)
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        qualifies_by_age = (age < p.child_age) & ~filer_is_dependent
        # ... disability: a dependent (IRC 21(b)(1)(B), which ignores
        # 152(b)(1)) or, on a joint return, either spouse (21(b)(1)(C))
        # incapable of self-care, whichever spouse is labelled head.
        is_dependent = person("is_tax_unit_dependent", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        married = tax_unit("tax_unit_married", period)
        disabled = person("is_incapable_of_self_care", period)
        qualifies_by_disability = disabled & (is_dependent | (head_or_spouse & married))
        return tax_unit.sum(qualifies_by_age | qualifies_by_disability)
