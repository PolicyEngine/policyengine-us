from policyengine_us.model_api import *


class me_sales_tax_fairness_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Maine sales tax fairness credit"
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_ptfc_fillable.pdf#page=3",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # 36 MRSA 5213-A(6)(C) excludes individuals who may be claimed as a
        # dependent on another return, and subsection 2 allows each resident
        # individual the base credit for the return's filing status. On a
        # joint return where only one spouse can be claimed, the other spouse
        # still qualifies for the joint credit.
        independent_filer = (
            tax_unit("head_spouse_count_not_dependent_elsewhere", period) > 0
        )
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return independent_filer & ~separate
