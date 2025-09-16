from policyengine_us.model_api import *


class ssdi_months_waiting(Variable):
    value_type = int
    entity = Person
    label = "SSDI months in waiting period"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/423#c_2"
    documentation = """
    Number of months person has been in the SSDI 5-month waiting period.
    Benefits begin after the 5-month waiting period is complete.

    Per 42 USC 423(c)(2), no benefits are payable for the first 5 months
    of disability. Since PolicyEngine doesn't track disability onset dates,
    this is an input variable. Users should provide the number of full
    months since disability onset.
    """
    # Maybe we don't need this
