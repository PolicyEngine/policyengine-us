from policyengine_us.model_api import *


class pr_child_tax_credit(Variable):
    value_type = int
    entity = TaxUnit
    label = "Amount for Puerto Rico child tax credit"
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.child_tax_credit
        num_children = tax_unit("pr_child_tax_credit_number_eligible_children", period)

        return num_children * p.amount