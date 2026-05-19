from policyengine_us.model_api import *


class dc_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "DC deduction for each person in tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=44"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=44"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        tax_unit_deduction = person.tax_unit("dc_deduction_joint", period)
        person_agi = person("dc_agi", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        tax = parameters(period).gov.states.dc.tax.income

        head_agi = person.tax_unit.sum(person_agi * head)
        spouse_agi = person.tax_unit.sum(person_agi * spouse)
        head_allocation = allocate_joint_amount_to_minimize_combined_tax(
            tax.rates, head_agi, spouse_agi, tax_unit_deduction
        )
        spouse_allocation = tax_unit_deduction - head_allocation
        return where(head, head_allocation, where(spouse, spouse_allocation, 0))
