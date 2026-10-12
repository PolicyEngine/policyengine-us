from policyengine_us.model_api import *


class ct_child_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut child tax rebate"
    unit = USD
    definition_period = YEAR
    # Assumes 100% take-up: PA 22-118 Sec. 411(b)(3) required an electronic
    # application to DRS by 2022-07-31 (TSSB 2022-5 Q6), which PolicyEngine does
    # not model, so the 2021 aggregate is an upper bound. DRS's offset of the
    # rebate against outstanding tax debts (Q19) is likewise unmodeled.
    defined_for = StateCode.CT
    reference = (
        "https://cga.ct.gov/2022/ACT/PA/PDF/2022PA-00118-R00HB-05506-PA.PDF#page=548",
        "https://portal.ct.gov/-/media/drs/publications/tssb/2022/tssb-2022-5.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        # Statutory domicile test is 2022 domicile at application time
        # (Sec. 411(a)(2); TSSB 2022-5 Q10/Q18), approximated here by 2021 CT
        # residence via defined_for, matching the RI analogue.
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ct.tax.income.rebate

        reduction_start = p.reduction.start[filing_status]

        person = tax_unit.members
        # Age is measured at the period, not "as of December 31, 2021"
        # (Sec. 411(a)(1)); PE's age has no within-year date (PE-wide limitation).
        age = person("age", period)
        # is_tax_unit_dependent (structurally ~head & ~spouse) proxies
        # Sec. 411(b)(1)'s requirement that the child be validly claimed as a
        # dependent on the 2021 federal return.
        dependent = person("is_tax_unit_dependent", period)
        eligible_child = (age <= p.age_limit) & dependent
        count_children = tax_unit.sum(eligible_child)
        capped_children = min_(count_children, p.child_cap)
        total_rebate = capped_children * p.amount

        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / p.reduction.increment)
        # At exactly AGI $110,000 a single filer hits 10 increments x 10% = 100%
        # reduction = $0, which Sec. 411(b)(2) controls; TSSB 2022-5 Q12's "less
        # than or equal to $110,000" wording reads loosely but is not a discrepancy.
        reduction_share = min_(increments * p.reduction.rate, 1)

        return total_rebate * (1 - reduction_share)
