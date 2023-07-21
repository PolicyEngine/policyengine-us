from policyengine_us.model_api import *


class mi_exemption_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Michigan household exemption count"
    defined_for = StateCode.MI
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
        )


# todo: exemption calculation
