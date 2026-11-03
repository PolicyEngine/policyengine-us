from policyengine_us.model_api import *


class az_property_tax_credit_unemployment(Variable):
    value_type = float
    entity = Person
    label = "Unemployment compensation counted for the Arizona property tax credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "A household member's unemployment compensation paid under another "
        "state's law, which the Arizona property tax credit counts in full "
        "(Form 140PTC line I). It is at most the member's unemployment "
        "compensation. Arizona unemployment insurance payments are not income "
        "for the credit (ARS 43-1072(I)); az_property_tax_credit_agi and "
        "az_property_tax_credit_dependent_income take out all unemployment "
        "compensation that federal gross income holds, and this adds back the "
        "other states' part."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(I)
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
    ]
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        total = max_(person("total_unemployment_compensation", period), 0)
        other_state = max_(
            person("az_other_state_unemployment_compensation", period), 0
        )
        return min_(other_state, total)
