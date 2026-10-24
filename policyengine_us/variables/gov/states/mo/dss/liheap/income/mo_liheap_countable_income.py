from policyengine_us.model_api import *


class mo_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Missouri LIHEAP countable income"
    documentation = "Countable income of all members, including members left out of the household size as non-citizens, plus Missouri TANF, less court-ordered child support members pay to someone outside the household and the medical deduction. The child support input does not identify court orders, so all child support paid is deducted."
    reference = (
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/MO_Plan_2026.pdf#page=5",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/02/liheap-application.pdf#page=5",
        # PDF pages 2-3
        "https://www.sos.mo.gov/cmsimages/adrules/csr/current/13csr/13c40-19.pdf#page=2",
        # PDF pages 36, 42-43
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2025/10/liheap-policy-procedure-manual.pdf#page=36",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["mo_liheap_countable_income_person", "mo_tanf"])
        # The 2025 manual deducts child support "paid by any household member
        # to someone not included in the LIHEAP household" (page 36) and calls
        # members left out as non-citizens "ineligible household members"
        # (page 42), so their child support paid is deducted like that of
        # other members.
        deductions = add(
            spm_unit,
            period,
            ["child_support_expense", "mo_liheap_medical_deduction"],
        )
        return max_(income - deductions, 0)
