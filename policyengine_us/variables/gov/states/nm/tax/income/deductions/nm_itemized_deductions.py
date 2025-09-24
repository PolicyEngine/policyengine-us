from policyengine_us.model_api import *


class nm_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf"
    defined_for = StateCode.NM

    adds = ["total_itemized_taxable_income_deductions"]
