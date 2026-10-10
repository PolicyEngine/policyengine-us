from policyengine_us.model_api import *


class dc_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Whether the child is eligible for the DC CTC"
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        # D.C. Code 47-1806.17(a), (d): a child for whom the taxpayer is allowed
        # a deduction under IRC 151, claimed on the federal and District returns.
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.17",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.credits.ctc.child
        age = person("age", period)
        # A return on which the filer (or, if joint, either spouse) can be
        # claimed as a dependent has no dependents (IRC 152(b)(1)).
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        return (age < p.age_threshold) & ~filer_is_dependent
