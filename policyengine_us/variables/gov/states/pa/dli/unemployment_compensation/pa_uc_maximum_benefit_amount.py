from policyengine_us.model_api import *


class pa_uc_maximum_benefit_amount(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation maximum benefit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = "pa_uc_monetarily_eligible"

    def formula(person, period, parameters):
        # § 404(c): maximum benefit amount equals the weekly benefit rate
        # multiplied by the number of credit weeks up to twenty-six. The
        # dependent allowance is paid in addition to (not as part of) the
        # MBA per § 404(e)(3).
        wbr = person("pa_uc_weekly_benefit_rate", period)
        max_weeks = person("pa_uc_maximum_weeks", period)
        return wbr * max_weeks
