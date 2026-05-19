from policyengine_us.model_api import *


class nj_unemployment_insurance_base_period_wages(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance base period wages"
    unit = USD
    documentation = (
        "Total wages earned during the New Jersey UI base period. Phase-1 "
        "scope: the regular base period (first 4 of the last 5 completed "
        "calendar quarters) and the two alternate base periods defined in "
        "N.J.S.A. 43:21-19(c) are not derived in-model; callers should "
        "pre-aggregate base-period wages before inputting this amount."
    )
    definition_period = YEAR
    reference = "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf"
    defined_for = StateCode.NJ
