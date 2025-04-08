from policyengine_us.model_api import *


class pr_actc_eligibility(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Puerto Rico additional child tax credit eligiblity"
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040ss.pdf#page=2"

    def formula(tax_unit, period, parameters):
        num_children = tax_unit("ctc_qualifying_children", period)
        ctc_amount = tax_unit("pr_ctc", period)

        # eligibility: at least one child under age of 17, line 1
        num_children_eligible = num_children >= 1
        # must not have too high of an income, line 10
        income_eligible = tax_unit("pr_actc_modified_income_calculation") < ctc_amount
        
        return num_children_eligible & income_eligible