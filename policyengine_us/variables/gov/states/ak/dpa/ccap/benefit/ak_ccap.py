from policyengine_us.model_api import *


class ak_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alaska CCAP monthly benefit"
    definition_period = MONTH
    defined_for = "ak_ccap_eligible"
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=846",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=596",
    )

    def formula(spm_unit, period):
        # Manual §4370 describes the subsidy as
        # `min(provider charged rate, state max rate) - copay`.
        # In microsim we don't observe per-provider charged rates, so we
        # approximate the regulatory min(charged, max) with min(actual
        # childcare expenses the household pays, state max). This matches
        # the MA CCFA / CO CCAP / RI CCAP convention. We use
        # `spm_unit_pre_subsidy_childcare_expenses` (not `childcare_expenses`)
        # to avoid a cycle with state TANF programs.
        total_per_child = add(spm_unit, period, ["ak_ccap_benefit_per_child"])
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        copay = spm_unit("ak_ccap_copay", period)
        capped = min_(pre_subsidy_childcare_expenses, total_per_child)
        return max_(0, capped - copay)
