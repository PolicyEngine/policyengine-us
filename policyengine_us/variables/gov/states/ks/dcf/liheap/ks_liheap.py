from policyengine_us.model_api import *


class ks_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas LIEAP"
    documentation = "Annual Kansas Low Income Energy Assistance Program (LIEAP) heating benefit: the benefit matrix amount, subject to the minimum benefit. Verified for FY2025-2026; earlier results use model parameter backfilling and are unverified historical estimates."
    unit = USD
    definition_period = YEAR
    defined_for = "ks_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=9",
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13400.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13400.htm",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.payment
        matrix_amount = spm_unit("ks_liheap_matrix_amount", period)
        return max_(matrix_amount, p.min_benefit)
