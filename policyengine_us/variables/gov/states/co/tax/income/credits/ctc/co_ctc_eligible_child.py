from policyengine_us.model_api import *


class co_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Colorado child tax credit eligible child"
    definition_period = YEAR
    reference = (
        "https://leg.colorado.gov/sites/default/files/2023a_1112_signed.pdf#page=2",
        # Income Tax Topics: Child Tax Credit (January 2026): each child must
        # "meet the requirements for the federal child tax credit".
        "https://tax.colorado.gov/sites/tax/files/documents/ITT_Child_Tax_Credit_Jan_2026.pdf#page=2",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.ctc
        child = add(person, period, p.eligible_child) > 0
        # The child must be one the taxpayer claims as a dependent. A return on
        # which the filer (or, if joint, either spouse) can be claimed as a
        # dependent has no dependents (IRC 152(b)(1)).
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        return child & ~filer_is_dependent
