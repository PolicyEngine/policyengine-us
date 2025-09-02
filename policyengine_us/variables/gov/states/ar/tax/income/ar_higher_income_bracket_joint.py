from policyengine_us.model_api import *


class ar_higher_income_bracket_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas income tax before non refundable credits when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.rates.main
        taxable_income = person("ar_taxable_income_joint", period)
        return p.higher_income_brackets.brackets.calc(taxable_income)
