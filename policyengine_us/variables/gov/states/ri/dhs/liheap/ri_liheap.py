from policyengine_us.model_api import *


class ri_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Rhode Island LIHEAP direct-heating assistance"
    defined_for = "ri_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf",
        "https://ripuc.ri.gov/eventsactions/docket/4290-DHS-DR-PUC%203-6%20attachment%20LIHEAP%20Manual%202020%20-%20Final.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        payment = spm_unit("ri_liheap_base_payment", period)
        # Heat-in-rent eligibility is modeled, but the rule selecting its
        # direct or secondary-electric payment is unresolved. Its zero here
        # denotes an unmodeled award, not legal ineligibility.
        return where(heat_in_rent, 0, payment)
