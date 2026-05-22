from policyengine_us.model_api import *


class pa_uc_credit_weeks(Variable):
    """A credit week per § 4(g.1) is a calendar week in which earnings meet
    or exceed credit_week_minimum_earnings ($116 in 2025, equal to 16 times
    the state minimum wage). PolicyEngine cannot simulate per-week earnings
    from annual data, so this is a direct input rather than a derived value;
    the credit_week_minimum_earnings parameter is documentary.
    """

    value_type = int
    entity = Person
    label = "Pennsylvania unemployment compensation credit weeks"
    unit = "week"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=16",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=17",
    )
    defined_for = StateCode.PA
