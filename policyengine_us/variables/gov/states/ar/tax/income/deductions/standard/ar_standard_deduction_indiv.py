from policyengine_us.model_api import *


class ar_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas standard deduction when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.states.ar.tax.income.deductions
        return head_or_spouse * p.standard[filing_status]
