from policyengine_us.model_api import *


class is_dependent_elsewhere_without_filing_exception(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Claimable elsewhere without the claimant filing exception"
    documentation = (
        "Whether the person is claimable as a dependent on another return "
        "and the would-be claimant does not meet the nonrequired-filing "
        "exception. Used for childless EITC and the Dependent Taxpayer Test."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(person, period, parameters):
        return person("claimable_as_dependent_on_another_return", period) & ~person(
            "dependent_claimant_filing_exception", period
        )
