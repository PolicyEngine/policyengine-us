from policyengine_us.model_api import *


class ar_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        agi = tax_unit("ar_agi", period)
        head = person("is_tax_unit_head", period)
        person_agi = person("ar_agi_person", period)
        total_head_agi = tax_unit.sum(person_agi * head)

        ar_itemized_deds = tax_unit("ar_itemized_deductions_sources", period)

        # Prorated itemized deductions only apply to married filers filing separately
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        prorate = np.zeros_like(agi)
        mask = agi > 0
        prorate[mask] = total_head_agi[mask] / agi[mask]
        prorated_itemized_deductions = ar_itemized_deds * prorate

        return where(separate, prorated_itemized_deductions, ar_itemized_deds)
