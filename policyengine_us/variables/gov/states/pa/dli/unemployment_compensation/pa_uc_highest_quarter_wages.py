from policyengine_us.model_api import *


class pa_uc_highest_quarter_wages(Variable):
    """Wages paid in the claimant's highest base-year quarter, used as the
    rate-table x-axis per § 404(e)(1). PolicyEngine cannot derive this from
    annual data, so this is a direct input rather than a computed value;
    populate via test fixtures or reform.
    """

    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation highest quarter wages"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=136",
    )
    defined_for = StateCode.PA
