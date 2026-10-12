from policyengine_us.model_api import *


class tn_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Tennessee CCAP benefit amount"
    definition_period = MONTH
    defined_for = "tn_ccap_eligible"
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/Reimbursement_Rate_Chart_1.1.26.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap
        if not p.in_effect:
            return 0

        copay = spm_unit("tn_ccap_copay", period)
        # The rate chart sets a separate weekly rate for each child, from that
        # child's age category, provider type, county tier, and QRIS tier, so
        # the lesser-of comparison applies per child before summing. Pooling
        # the caps first would let one child's unused rate headroom cover
        # another child's above-rate charges.
        person = spm_unit.members
        max_weekly_benefit = person("tn_ccap_max_weekly_benefit", period)
        max_monthly_benefit = max_weekly_benefit * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        # Per-child share of the family's childcare expenses. Ineligible
        # children draw a zero rate through tn_ccap_max_weekly_benefit's
        # defined_for, so they contribute nothing.
        child_expenses = person("pre_subsidy_childcare_expenses", period)
        # Reimbursement is the lesser of the provider charge and the state rate,
        # less the parent copay.
        capped_expenses = spm_unit.sum(min_(child_expenses, max_monthly_benefit))
        return max_(capped_expenses - copay, 0)
