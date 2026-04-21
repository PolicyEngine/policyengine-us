from policyengine_us.model_api import *


class pa_uc(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = "pa_uc_monetarily_eligible"

    def formula(person, period, parameters):
        # Annual benefit equals the weekly payable amount multiplied by the
        # number of weeks for which benefits are claimed, capped at the
        # maximum weeks of entitlement under § 404(c).
        weekly_payable = person("pa_uc_weekly_payable", period)
        maximum_weeks = person("pa_uc_maximum_weeks", period)
        weeks_unemployed = person("pa_uc_weeks_unemployed", period)
        weeks_paid = min_(weeks_unemployed, maximum_weeks)
        return weekly_payable * weeks_paid
