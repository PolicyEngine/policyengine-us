from policyengine_us.model_api import *


class me_fairness_credit_qualifying_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Maine sales and property tax fairness credit qualifying children and dependents"
    documentation = (
        "Number of qualifying children and dependents for whom the filer can "
        "claim a federal credit under IRC section 24 (the Child Tax Credit or "
        "the credit for other dependents), for the Maine sales tax and "
        "property tax fairness credits."
    )
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = (
        # 36 MRSA 5213-A(1)(A-1)(2).
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",
        # 36 MRSA 5219-KK(1)(A-1)(2) and (3).
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",
        # 2025 Form 1040ME Instructions, line 13a, Property Tax Fairness
        # Credit and Sales Tax Fairness Credit. PDF pages 5, 11.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_gen_instr_w_cover_pg.pdf#page=5",
        # 2025 Schedule PTFC/STFC, line 8, line 17 and instructions.
        # PDF pages 2-4.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_ptfc_fillable.pdf#page=2",
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
        # 24 includes the credit for other dependents of IRC 24(h)(4), and the
        # Form 1040ME line 13a instructions count each dependent for whom the
        # filer is eligible to claim "the federal child tax credit or the
        # credit for other dependents". So a dependent counts when either
        # credit is allowed for that person before the phase-out: a child
        # under 17, a child with an ITIN but no SSN, a child whose filer fails
        # the Child Tax Credit SSN rule (IRC 24(h)(4)(C)), or an older
        # dependent. The dependent and the filer still need a TIN (IRC 24(e)).
        # The credit for other dependents starts in 2018, so earlier years
        # count only Child Tax Credit children.
        section_24_amount = person("ctc_individual_maximum", period)
        return tax_unit.sum(section_24_amount > 0)
