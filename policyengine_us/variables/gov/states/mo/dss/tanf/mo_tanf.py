from policyengine_us.model_api import *


class mo_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        # 13 CSR 40-2.310(14): payments lowered to the whole dollar; no
        # payment below $10.
        "https://www.sos.mo.gov/cmsimages/adrules/csr/current/13csr/13c40-2.pdf#page=36",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-15/",
    )
    defined_for = "mo_tanf_eligible"

    def formula(spm_unit, period, parameters):
        maximum_benefit = spm_unit("mo_tanf_maximum_benefit", period)
        countable_income = spm_unit("mo_tanf_countable_income", period)
        benefit = max_(maximum_benefit - countable_income, 0)
        capped_benefit = min_(benefit, maximum_benefit)
        p = parameters(period).gov.states.mo.dss.tanf
        # 13 CSR 40-2.310(14): "In the payment of TA benefits, the amount
        # shall always be lowered to the nearest dollar interval", and a
        # grant below $10 is not paid.
        payment = np.floor(capped_benefit)
        return where(payment >= p.minimum_payment, payment, 0)
