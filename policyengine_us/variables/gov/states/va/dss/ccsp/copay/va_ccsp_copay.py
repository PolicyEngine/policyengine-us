from policyengine_us.model_api import *


class va_ccsp_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Virginia Child Care Subsidy Program family copayment"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = (
        "https://doe.virginia.gov/home/showpublisheddocument/56270#page=69",
        "https://doe.virginia.gov/home/showpublisheddocument/56270#page=143",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.ccsp.copay
        countable_income = spm_unit("va_ccsp_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)

        # FPG ratio for copay bracket lookup
        fpg_ratio = np.divide(
            countable_income,
            fpg,
            out=np.zeros_like(countable_income),
            where=fpg > 0,
        )
        per_child_copay = p.per_child_scale.calc(fpg_ratio)

        # Count eligible children actually in care, capped at max_children
        person = spm_unit.members
        eligible_child = person("va_ccsp_child_eligible", period)
        attending = person("childcare_attending_days_per_month", period.this_year) > 0
        n_eligible_children = spm_unit.sum(eligible_child & attending)
        n_assessed = min_(n_eligible_children, p.max_children)

        # Total from scale
        total_from_scale = per_child_copay * n_assessed

        # Income cap
        income_cap = countable_income * p.income_cap_rate
        family_copay = min_(total_from_scale, income_cap)

        # TANF recipients exempt from copay
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return where(is_tanf, 0, family_copay)
