from policyengine_us.model_api import *


class pa_uc_partial_benefit_credit(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation partial benefit credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=34",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        # § 4(m.3): Partial Benefit Credit = the greater of 30% of the
        # weekly benefit rate or $6, rounded up to the next higher dollar.
        wbr = person("pa_uc_weekly_benefit_rate", period)
        p = parameters(
            period
        ).gov.states.pa.dli.unemployment_compensation.partial_benefit_credit
        # Round before ceil to avoid float32 precision issues (e.g. 100 * 0.3
        # stored as 30.0000001 would otherwise ceil to 31).
        uncapped = max_(np.round(wbr * p.rate, 4), p.minimum)
        return np.ceil(uncapped)
