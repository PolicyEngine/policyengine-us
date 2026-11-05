from policyengine_us.model_api import *


class az_other_state_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "Unemployment compensation paid under another state's law"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "The part of a person's unemployment compensation paid under the "
        "unemployment insurance law of a state other than Arizona. The Arizona "
        "property tax credit excludes Arizona unemployment insurance payments "
        "from household income (ARS 43-1072(I)) but counts other states' "
        "payments (2025 Form 140PTC instructions, line I). The rest of "
        "unemployment compensation is treated as paid under Arizona law, as a "
        "claimant must be a full-year Arizona resident (ARS 43-1072(H)(1))."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(H)(1), (I)
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
    ]
