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
        # The above references say the following:
        # "You may allocate this [tax-unit deduction] amount as you wish."
        # Here we allocate in proportion to head and spouse DC AGI
        person_agi = person("dc_agi", period)
        tax_unit_agi = person.tax_unit.sum(person_agi)
        share = np.zeros_like(tax_unit_agi)
        mask = tax_unit_agi > 0
        share[mask] = person_agi[mask] / tax_unit_agi[mask]
        return share * tax_unit_deduction
