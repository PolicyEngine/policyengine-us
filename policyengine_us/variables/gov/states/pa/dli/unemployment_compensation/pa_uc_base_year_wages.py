from policyengine_us.model_api import *


class pa_uc_base_year_wages(Variable):
    """Total wages paid to the claimant in the four-quarter "base year" used
    for monetary determination per § 401(a)(2). PolicyEngine cannot derive
    this from annual data without strong assumptions, so this is a direct
    input rather than a computed value; populate via test fixtures or reform.
    """

    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation base year wages"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=119",
    )
    defined_for = StateCode.PA
