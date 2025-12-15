from policyengine_us.model_api import *


class mt_agi_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana AGI for joint filers (tax unit level)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    documentation = "Montana AGI calculated at tax unit level for joint filers, pooling income and subtractions before applying them"

    def formula(tax_unit, period, parameters):
        # Pool federal AGI at tax unit level
        agi = add(tax_unit, period, ["adjusted_gross_income_person"])

        # Pool Montana additions at tax unit level
        additions = add(tax_unit, period, ["mt_additions"])

        # Pool Montana subtractions at tax unit level
        # This allows spouse's subtractions to offset head's income
        subtractions = add(tax_unit, period, ["mt_subtractions"])

        # Apply pooled subtractions to pooled income
        reduced_agi = max_(agi + additions - subtractions, 0)

        # Montana taxable social security benefits can be either addition or subtraction
        # if mt_taxable_social_security - taxable_social_security > 0, then addition, else subtraction

        p = parameters(period).gov.states.mt.tax.income.social_security
        if p.applies:
            # 2023 and before: apply lines 21-24 adjustment for social security
            taxable_ss = add(tax_unit, period, ["taxable_social_security"])
            mt_taxable_ss = add(
                tax_unit, period, ["mt_taxable_social_security"]
            )
            adjusted_mt_ss_difference = mt_taxable_ss - taxable_ss
            tax_unit_mt_agi = max_(reduced_agi + adjusted_mt_ss_difference, 0)
        else:
            # 2024 and after: no longer apply the social security adjustment
            tax_unit_mt_agi = reduced_agi

        return tax_unit_mt_agi
