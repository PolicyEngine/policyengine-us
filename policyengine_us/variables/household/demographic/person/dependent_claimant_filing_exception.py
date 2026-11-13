from policyengine_us.model_api import *


class dependent_claimant_filing_exception(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Dependent's would-be claimant meets the filing exception"
    documentation = (
        "Whether the person who could claim this person (all such claimants "
        "if more than one) is not required to file an income tax return and "
        "either files no return or files solely to obtain a refund of income "
        "tax withheld or estimated tax paid. A return filed to claim refundable "
        "tax credits, including EITC, does not qualify. This fact permits EITC and claiming "
        "one's own dependents under the Dependent Taxpayer Test; it does not "
        "remove general claimability or its standard-deduction limitation."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )
