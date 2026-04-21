from policyengine_us.model_api import *


class pa_uc_weekly_payable(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation weekly payable amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = "pa_uc_monetarily_eligible"

    def formula(person, period, parameters):
        # § 404(d)(1): weekly compensation equals the weekly benefit rate
        # less earnings above the partial benefit credit, floored at 0,
        # plus the dependent allowance.
        wbr = person("pa_uc_weekly_benefit_rate", period)
        pbc = person("pa_uc_partial_benefit_credit", period)
        earnings = person("pa_uc_gross_weekly_earnings", period)
        dependent_allowance = person("pa_uc_dependent_allowance", period)
        earnings_reduction = max_(earnings - pbc, 0)
        base_benefit = max_(wbr - earnings_reduction, 0)
        return base_benefit + dependent_allowance
