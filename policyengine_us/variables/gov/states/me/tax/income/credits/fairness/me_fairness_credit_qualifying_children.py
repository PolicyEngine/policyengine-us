from policyengine_us.model_api import *


class me_fairness_credit_qualifying_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Maine sales and property tax fairness credit qualifying children"
    documentation = (
        "Number of qualifying children for whom the filer can claim a federal "
        "credit under IRC section 24 (the Child Tax Credit or the credit for "
        "other dependents), for the Maine sales tax and property tax fairness "
        "credits."
    )
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = (
        # 36 MRSA 5213-A(1)(A-1)(2).
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",
        # 36 MRSA 5219-KK(1)(A-1)(2) and (3).
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",
        # 2025 Instructions for Schedule 8812, TIN Required by Due Date of
        # Your Return To Claim the ODC, and Credit for Other Dependents.
        # PDF pages 1-2.
        "https://www.irs.gov/pub/irs-prior/i1040s8--2025.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # 36 MRSA 5213-A(1)(A-1)(2) and 5219-KK(1)(A-1)(2)-(3) count each
        # "qualifying child or dependent" for whom the filer "can claim the
        # federal child tax credit pursuant to the Code, Section 24". Section
        # 24 includes the credit for other dependents of IRC 24(h)(4), and IRC
        # 24(h)(4)(C) gives that credit for a child whose Child Tax Credit is
        # denied by the social security number rule of IRC 24(h)(7). So a
        # child whose filer fails the Child Tax Credit identification test
        # still counts when the filer meets the taxpayer identification test
        # for the credit for other dependents. Dependents who are not CTC
        # qualifying children are not counted here.
        qualifying_child = person(
            "ctc_qualifying_child_ignoring_filer_identification", period
        )
        filer_meets_identification_requirements = tax_unit(
            "filer_meets_ctc_identification_requirements", period
        )
        return tax_unit.sum(qualifying_child) * filer_meets_identification_requirements
