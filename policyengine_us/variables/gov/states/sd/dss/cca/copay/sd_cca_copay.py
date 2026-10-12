from policyengine_us.model_api import *

# Floating-point guard for the whole-dollar floor, not a policy value: it
# prevents exact whole-dollar results represented infinitesimally below the
# integer from flooring to the prior dollar.
ROUNDING_GUARD = 1e-4


class sd_cca_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "South Dakota CCA family co-payment"
    definition_period = MONTH
    defined_for = "sd_cca_eligible"
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/BEES_CCA_Policy_Manual.pdf#page=42",
        "https://dss.sd.gov/docs/childcare/assistance/Sliding_Fee_Scale.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.copay
        # Income is floored at zero so a self-employment loss cannot produce a
        # negative co-payment.
        countable_income = max_(spm_unit("sd_cca_countable_income", period), 0)
        # spm_unit_fpg is an annual dollar amount; the bare monthly period
        # auto-divides it to a monthly value.
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        # The co-payment is 5% of countable income above 170% of the federal
        # poverty level, and zero at or below that threshold.
        income_above_threshold = max_(
            countable_income - p.fpl_threshold * monthly_fpg, 0
        )
        copay = income_above_threshold * p.rate
        # The co-payment never exceeds 12% of countable income.
        copay = min_(copay, p.max_rate * countable_income)
        # BEES Section 9.2 rounds the monthly co-payment down to a whole dollar.
        copay = np.floor(copay + ROUNDING_GUARD)
        # TANF enrollment waives the family co-payment. Foster and protective-
        # services waivers are child-specific: the family amount remains when
        # any ordinary eligible child is covered, and is zero only when all
        # eligible covered children qualify for a child-based waiver.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        person = spm_unit.members
        is_eligible_child = person("sd_cca_eligible_child", period)
        receives_child_based_waiver = person("is_in_foster_care", period) | person(
            "receives_or_needs_protective_services", period.this_year
        )
        has_waived_eligible_child = (
            spm_unit.sum(is_eligible_child & receives_child_based_waiver) > 0
        )
        has_non_waived_eligible_child = (
            spm_unit.sum(is_eligible_child & ~receives_child_based_waiver) > 0
        )
        child_based_waiver = has_waived_eligible_child & ~has_non_waived_eligible_child
        waived = is_tanf_enrolled | child_based_waiver
        return where(waived, 0, copay)
