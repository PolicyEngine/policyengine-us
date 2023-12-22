from policyengine_us.model_api import *


class ar_itemized_deductions(Variable):
    value_type = float
    entity = Person
    label = "Arkansas itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR3_ItemizedDeduction.pdf"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        unit_deds = person.tax_unit("ar_itemized_deductions_unit", period)
        agi = person.tax_unit("ar_agi", period)
        head = person("is_tax_unit_head", period)
        person_agi = person("ar_agi_person", period)
        total_head_agi = person_agi * head

        prorate = np.zeros_like(agi)
        mask = agi > 0
        prorate[mask] = total_head_agi[mask] / agi[mask]
        return unit_deds * prorate
