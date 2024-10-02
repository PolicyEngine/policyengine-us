from policyengine_us.model_api import *


class de_base_standard_deduction_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware base standard deduction when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.states.de.tax.income.deductions.standard
        return head_or_spouse * p.amount[filing_status]
