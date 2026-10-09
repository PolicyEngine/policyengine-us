from policyengine_us.model_api import *


class ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "CTC-qualifying child"
    documentation = "Child qualifies for the Child Tax Credit"
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#c",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
        # Publication 501, Dependent Taxpayer Test.
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.irs.credits.ctc
        age_limit = p.amount.base.thresholds[-1]
        age_eligible = age < age_limit
        meets_identification_requirements = person(
            "meets_ctc_child_identification_requirements", period
        )
        # IRC 24(a) allows the credit only for a qualifying child for whom the
        # taxpayer is allowed a deduction under section 151. Under IRC
        # 152(b)(1) a taxpayer who can be claimed as a dependent is treated as
        # having no dependents, and on a joint return neither spouse may be
        # claimable (Publication 501, Dependent Taxpayer Test).
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        return age_eligible & meets_identification_requirements & ~filer_is_dependent
