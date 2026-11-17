from policyengine_us.model_api import *


class wa_pte_assessment_year_age(Variable):
    value_type = float
    entity = Person
    unit = "year"
    label = "Age attained at the end of the preceding Washington property tax assessment year"
    quantity_type = STOCK
    definition_period = YEAR
    default_value = -1
    defined_for = StateCode.WA
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2023-24/Htm/Bills/Session%20Laws/House/1355-S.SL.htm",  # RCW 84.36.381(3)(a)(i) as applicable to 2025 collection
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-130",  # (2)(a)
    )
