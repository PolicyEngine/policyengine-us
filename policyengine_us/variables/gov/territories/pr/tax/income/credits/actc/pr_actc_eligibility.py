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
        excess_ss_tax = tax_unit("pr_excess_social_security_withheld", period)
        taxes_paid = tax_unit("pr_actc_sum_taxes_paid", period)

        # eligibility: at least one child under age of 17, line 1
        num_children_eligible = num_children >= 1
        # must not have too high of an income, line 10
        # if modified agi < threshold, modified income calculation = 0, therefore this will be true
        income_eligible = (
            tax_unit("pr_actc_modified_income_calculation", period)
            < ctc_amount
        )
        # taxes paid must be greater than excess social security tax withheld, line 18
        taxes_paid_eligible = taxes_paid > excess_ss_tax

        return num_children_eligible & income_eligible & taxes_paid_eligible
