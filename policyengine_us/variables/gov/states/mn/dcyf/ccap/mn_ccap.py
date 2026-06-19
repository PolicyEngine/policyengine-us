from policyengine_us.model_api import *


class mn_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Minnesota CCAP benefit amount"
    definition_period = MONTH
    defined_for = "mn_ccap_eligible"
    reference = (
        # Minnesota CCAP Policy Manual section 9.9; Minn. Stat. 142E.17 subd. 1.
        "https://www.revisor.mn.gov/statutes/cite/142E.17",
    )

    def formula(spm_unit, period, parameters):
        # The subsidy pays the lower of the family's actual child care expenses
        # or the sum of each eligible child's maximum rate (including any
        # quality differential), less the family copayment, floored at zero.
        # Capping at actual expenses also caps the quality differential at the
        # provider's charge.
        total_max_rate = add(spm_unit, period, ["mn_ccap_max_rate"])
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, total_max_rate)
        copay = spm_unit("mn_ccap_copay", period)
        subsidy = max_(capped_expenses - copay, 0)
        # The program also pays the provider's registration fee on the family's
        # behalf, where charged (optional input, default $0).
        registration_fee = spm_unit("mn_ccap_registration_fee", period)
        return subsidy + registration_fee
