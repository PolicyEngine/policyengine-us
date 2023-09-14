from policyengine_us.model_api import *


class mi_standard_allowance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan home heating credit standard allowance"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowance"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit.standard_allowance
        # determine count of exemption
        mi_exemption_count = tax_unit("exemptions", period)
        mi_taxable_income = tax_unit("mi_taxable_income", period)
        # additional income ceiling and standard allowance amount for over six exemptions
        additional_ceiling = p.additional_exemption.income * max_(
            (mi_exemption_count - p.additional_exemption.limit), 0
        )
        additional_allowance = p.additional_exemption.allowance * max_(
            (mi_exemption_count - p.additional_exemption.limit), 0
        )
        # determine standard allowance
        return where(
            mi_taxable_income
            <= p.income_base.calc(mi_exemption_count) + additional_ceiling,
            p.exemption_base.calc(mi_exemption_count) + additional_allowance,
            0,
        )

        
