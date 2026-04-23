from policyengine_us.model_api import *


class nj_unemployment_insurance_base_period_weeks(Variable):
    value_type = int
    entity = Person
    label = "New Jersey unemployment insurance qualifying base weeks in the base period"
    unit = "week"
    documentation = (
        "Count of base-period weeks that already satisfy New Jersey's "
        "base-week earnings threshold. Callers should pre-filter raw weeks "
        "using the applicable per-week minimum wage amount before inputting "
        "this count."
    )
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/title-43/section-43-21-19/"
    defined_for = StateCode.NJ
