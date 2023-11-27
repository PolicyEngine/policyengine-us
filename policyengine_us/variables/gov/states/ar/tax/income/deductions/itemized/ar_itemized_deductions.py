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
        year = period.start.year
        
        # We need to include this condition to be able to test the medical expense rate
        # as the itemized deductions list currently only back dates to 2018

        if year < 2018:
            instant_str = f"2018-01-01"
        else:
            instant_str = f"{year}-01-01"
        p_ded = parameters(instant_str).gov.irs.deductions

        agi = tax_unit("ar_agi", period)
        head = person("is_tax_unit_head", period)
        person_agi = person("ar_agi_person", period)
        total_person_agi = tax_unit.sum(person_agi * head)

        # Less salt deduction
        deductions = [
            deduction
            for deduction in p_ded.itemized_deductions
            if deduction
            not in [
                "salt_deduction",
                "medical_expense_deduction",
            ]
        ]
        less_salt_deds = add(tax_unit, period, deductions)

        # Real estate tax + Personal property tax
        real_estate_deds = add(tax_unit, period, ["real_estate_taxes"])

        ar_itemized_deds = tax_unit("ar_itemized_deductions_sum", period)

        total_itemized_deduction = (
            less_salt_deds + real_estate_deds + ar_itemized_deds
        )

        # Prorated itemized deductions
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        prorate = np.zeros_like(agi)
        mask = agi > 0
        prorate[mask] = total_person_agi[mask] / agi[mask]
        separated_itemized_deduction = total_itemized_deduction * prorate

        return where(
            separate, separated_itemized_deduction, total_itemized_deduction
        )
