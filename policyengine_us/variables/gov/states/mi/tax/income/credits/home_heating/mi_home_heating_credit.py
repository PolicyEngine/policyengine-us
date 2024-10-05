from policyengine_us.model_api import *


class mi_home_heating_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan home heating credit"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
    )

    def formula(tax_unit, period, parameters):
        standard_credit = tax_unit("mi_standard_home_heating_credit", period)
        alternate_credit = tax_unit("mi_alternate_home_heating_credit", period)
        p = parameters(period).gov.states.mi.tax.income.credits.home_heating
        larger_credit = max_(standard_credit, alternate_credit)
        total_credit = larger_credit * p.credit_percentage
        rate = tax_unit("mi_home_heating_credit_eligible_rate", period)
        return total_credit * rate
