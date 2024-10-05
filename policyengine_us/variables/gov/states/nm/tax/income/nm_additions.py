from policyengine_us.model_api import *


class nm_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/2f1a6781-9534-4436-b427-1557f9592099/2022pit-adj-ins.pdf",
    )
    defined_for = StateCode.NM
