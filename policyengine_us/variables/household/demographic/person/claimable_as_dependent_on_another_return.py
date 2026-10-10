from policyengine_us.model_api import *


class claimable_as_dependent_on_another_return(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Can be claimed as a dependent elsewhere"
    documentation = (
        "Whether another taxpayer, in another tax unit, can claim the person "
        "as a dependent: a "
        "deduction under IRC section 151 for the person is allowable to "
        "another taxpayer, whether or not claimed. Defaults to the actual "
        "or expected claim input for compatibility with existing callers. "
        "The dependent_claimant_filing_exception does not change this fact "
        "or the dependent standard-deduction limit."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/151#c",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=24",
    )

    def formula(person, period, parameters):
        return person("claimed_as_dependent_on_another_return", period)
