from policyengine_us.model_api import *


class de_pension_exclusion_domicile_requirement_met(Variable):
    value_type = bool
    entity = Person
    label = "Meets Delaware's domicile requirement for the pension exclusion at age 60 or older"
    documentation = (
        "Whether this person has lived in Delaware long enough to claim the "
        "pension exclusion at age 60 or older: at least 3 years of Delaware "
        "domicile for a person domiciled in Delaware before January 1, 2027, "
        "and at least 5 years for one domiciled there on or after that date. "
        "A person counts as domiciled in Delaware while a resident individual "
        "under 30 Del. C. 1103. PolicyEngine assumes the requirement is met "
        "unless this input says otherwise."
    )
    definition_period = YEAR
    default_value = True
    reference = (
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
        "https://legis.delaware.gov/json/BillDetail/GenerateHtmlDocument?legislationId=143006&legislationTypeId=5&docTypeId=2&legislationName=SA1",
    )
