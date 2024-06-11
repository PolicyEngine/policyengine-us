from policyengine_us.model_api import *


class ar_income_tax_before_non_refundable_credits_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas income tax before non refundable credits when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.rates.main
        taxable_income = person("ar_taxable_income_indiv", period)
        main_rate = p.rate.calc(taxable_income)
        pre_reduction_tax = main_rate * taxable_income
        reduction = p.reduction.calc(taxable_income)
        return max_(pre_reduction_tax - reduction, 0)
