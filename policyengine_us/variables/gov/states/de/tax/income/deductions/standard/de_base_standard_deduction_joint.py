from policyengine_us.model_api import *


class de_base_standard_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Delaware base standard deduction when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        filing_status = person.tax_unit("filing_status", period)
        is_head = person("is_tax_unit_head", period)
        p = parameters(period).gov.states.de.tax.income.deductions.standard
        return is_head * p.amount[filing_status]
