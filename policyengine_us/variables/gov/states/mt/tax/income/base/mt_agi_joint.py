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
        federal_agi = add(tax_unit, period, ["adjusted_gross_income_person"])

        # Pool Montana additions at tax unit level
        additions = add(tax_unit, period, ["mt_additions"])

        # Pool Montana subtractions at tax unit level
        # This allows spouse's subtractions to offset head's income
        subtractions = add(tax_unit, period, ["mt_subtractions"])

        # Apply pooled subtractions to pooled income
        mt_agi = max_(federal_agi + additions - subtractions, 0)

        # Apply social security adjustment if applicable (2021-2023)
        p = parameters(period).gov.states.mt.tax.income.social_security
        if p.applies:
            taxable_ss = add(tax_unit, period, ["taxable_social_security"])
            mt_taxable_ss = add(
                tax_unit, period, ["mt_taxable_social_security"]
            )
            ss_adjustment = mt_taxable_ss - taxable_ss
            return max_(mt_agi + ss_adjustment, 0)
        else:
            return mt_agi
