from policyengine_us.model_api import *


class dc_medicaid_immigration_eligible(Variable):
    value_type = bool
    entity = Person
    label = "DC Medicaid immigration eligible"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = [
        "https://dhcf.dc.gov/alliance",
        "https://dhcf.dc.gov/sites/default/files/dc/sites/dhcf/publication/attachments/Alliance%20and%20ICP%20Program%20Changes%20Resource%20Document.pdf",
    ]
    documentation = (
        "DC's Health Care Alliance program covers immigrants regardless of "
        "status, including undocumented immigrants, DACA recipients, TPS holders, "
        "and other immigration statuses not eligible for federal Medicaid."
    )

    def formula(person, period, parameters):
        # DC covers all immigrants regardless of status when they're not
        # already covered by federal Medicaid
        # Check if person would be categorically eligible for federal Medicaid
        federal_category = person("medicaid_category", period)
        federally_eligible = (
            federal_category != federal_category.possible_values.NONE
        )
        # If already federally eligible, they don't need DC coverage
        # If not federally eligible, DC will cover them
        return ~federally_eligible