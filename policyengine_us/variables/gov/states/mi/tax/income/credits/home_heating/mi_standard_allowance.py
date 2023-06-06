from policyengine_us.model_api import *


class mi_standard_allowance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan home heating credit standard allowance"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
       
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
         p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating.standard.allowance
        # determine count of exemption
        count = tax_unit("exemption_count", period)
        income = tax_unit("mi_taxable_income", period)
        # additional income ceiling and standard allowance amount for over six exemptions
        additional_ceiling = p.additional_income * (count - p.additional_exemption_limit)
        additional_allowance = p.additional_allowance * (count - p.additional_exemption_limit)
        # determine standard allowance
         return where(
            income <= p.income_base.amount.calc(count) + additional_ceiling,
            p.exemption_base.amount.calc(count) + additional_allowance,
            0
        )



       
