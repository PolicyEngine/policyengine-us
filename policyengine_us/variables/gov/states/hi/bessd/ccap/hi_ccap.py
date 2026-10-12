from policyengine_us.model_api import *


class hi_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Hawaii CCAP benefit amount"
    definition_period = MONTH
    defined_for = "hi_ccap_eligible"
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=28"

    def formula(spm_unit, period, parameters):
        # Maximum monthly payment = lesser of the department's Exhibit I rate
        # and the family's actual childcare cost (HAR 17-798.2-13(a),
        # 17-798.2-14(b)). pre_subsidy_childcare_expenses is YEAR-defined;
        # reading it with the bare monthly period auto-divides it to monthly.
        maximum_monthly_rate = add(spm_unit, period, ["hi_ccap_maximum_monthly_rate"])
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, maximum_monthly_rate)
        # Subsidy = lesser-of amount minus the family co-payment, floored at
        # zero (HAR 17-798.2-14(b)).
        copay = spm_unit("hi_ccap_copay", period)
        return max_(capped_expenses - copay, 0)
