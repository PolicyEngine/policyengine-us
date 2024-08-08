from policyengine_us.model_api import *


class denver_property_tax_relief(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Denver Property Tax Relief"
    definition_period = YEAR
    reference = "https://denvergov.org/files/content/public/v/37/government/agencies-departments-offices/agencies-departments-offices-directory/denver-human-services/be-supported/additional-assistance/property-tax-relief/denver-property-tax-relief-program-year-2021-rules.pdf"

    adds = [
        "co_de_property_tax_relief_homeowner",
        "co_de_property_tax_relief_renter",
    ]
