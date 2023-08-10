from policyengine_us.model_api import *


class mi_rent_include_heating_cost(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Heating costs are included in the amount rent calculation"
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
        )
