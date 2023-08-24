from policyengine_us.model_api import *


class ar_post_secondary_education_tuition_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas post-secondary education tuition deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized.post_secondary_education_tuition_deductions
        tuition_expense = tax_unit("qualified_tuition_expenses", period)
            
        return min(p.ratio*tuition_expense, p.two_year_college, p.four_year_college, p.technical_institutes)