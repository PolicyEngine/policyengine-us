from policyengine_us.model_api import *


class mi_heating_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household heating cost credit"
    defined_for = "mi_heating_credit_eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
    )

    def formula(tax_unit, period, parameters):
        standard_credit = tax_unit(
            "mi_home_heating_standard_credit", period
        )
        alternate_credit = tax_unit(
            "mi_alternate_heating_credit", period
        )
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating
        credit_percentage = p.credit_percentage
        return max_(standard_credit, alternate_credit) * credit_percentage
