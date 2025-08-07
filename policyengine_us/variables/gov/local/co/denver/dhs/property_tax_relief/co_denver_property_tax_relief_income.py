from policyengine_us.model_api import *


class co_denver_property_tax_relief_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Denver Property Tax Relief income"
    definition_period = YEAR
    reference = "https://denvergov.org/files/assets/public/v/2/denver-human-services/documents/property-tax-relief/dptr-instructions-2023.pdf#page=1"

    adds = "gov.local.co.denver.dhs.property_tax_relief.income_sources"
