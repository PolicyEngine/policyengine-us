from policyengine_us.model_api import *


class pa_uc_gross_weekly_earnings(Variable):
    """Gross earnings (cash + the cash value of in-kind compensation) for
    services performed in a week, used in § 4(u) and § 404(d)(1) to determine
    whether a claimant is "unemployed" for that week and to compute the
    partial-week payable. PolicyEngine has no per-week earnings concept, so
    this is a direct input; populate via test fixtures or reform.
    """

    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation gross weekly earnings"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = StateCode.PA
