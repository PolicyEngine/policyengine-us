from policyengine_us.model_api import *


class heating_cost(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total heating cost"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
        )
