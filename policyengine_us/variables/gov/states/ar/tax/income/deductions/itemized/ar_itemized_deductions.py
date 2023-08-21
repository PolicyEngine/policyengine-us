from policyengine_us.model_api import *


class ar_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        
        items = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        us_itm_deds_less_salt = add(tax_unit, period, items)
        filing_status = tax_unit("filing_status", period)
        capped_property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            p.itemized.salt_and_real_estate.cap[filing_status],
        )
        ar_itm_deds = us_itm_deds_less_salt + capped_property_taxes
        #######################
        
        agi = tax_unit("adjusted_gross_income",period)
        spouse_agi = tax_unit("spouse_separate_adjusted_gross_income",period)

        # Medical and dental expenses
        mde = tax_unit("medical_expense_deduction",period)

        # Real estate tax + Personal property tax
        rst = tax_unit("real_estate_taxes",period)

        # Interest Expense
        ied = tax_unit("interest_deduction",period)

        # Contributions
        contri = tax_unit("ira_contributions",period)  

        # Casualty and Theft Loss
        cl = tax_unit("casualty_loss_deduction",period) 

        # Post-secondary Education Tuition Deduction
        qte = tax_unit("qualified_tuition_expenses",period)
        

        # Miscellaneous Deductions 
        misc_deduc = tax_unit("misc_deduction",period)

        total_itemized_deduction = mde + + rst + ied + contri + cl + qte + misc_deduc

        # Prorated itemized deductions
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE

        separated_itemized_deduction = total_itemized_deduction*(agi/(agi + spouse_agi))

        return where(
            separate,
            separated_itemized_deduction,
            total_itemized_deduction
        )
        