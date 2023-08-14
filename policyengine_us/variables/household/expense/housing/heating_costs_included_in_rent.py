from policyengine_us.model_api import *


class heating_costs_included_in_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Michigan whether rent included in heating cost"
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
        )
