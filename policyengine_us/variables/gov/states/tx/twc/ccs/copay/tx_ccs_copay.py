from policyengine_us.model_api import *


class tx_ccs_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Texas Child Care Services (CCS) copayment"
    definition_period = MONTH
    reference = "https://wspanhandle.com/child-care/for-parents/"
    defined_for = "tx_ccs_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.copay

        # Get household income and SMI ratio
        income = spm_unit("tx_ccs_countable_income", period)
        smi = spm_unit("hhs_smi", period)
        income_to_smi_ratio = income / smi

        # Count eligible children in care
        eligible_children = spm_unit.sum(
            spm_unit.members("tx_ccs_eligible_child", period)
        )

        # Calculate copayment rates based on income bracket
        # Use Panhandle Region's values
        first_child_rate = p.rate.first_child.calc(income_to_smi_ratio)
        additional_child_rate = p.rate.additional_child

        # Calculate copayments as percentage of income
        first_child_copay = first_child_rate * income
        additional_children = max_(eligible_children - 1, 0)
        additional_copay = additional_child_rate * income * additional_children

        # Total copayment, capped at maximum rate
        total_copay = first_child_copay + additional_copay
        max_copay = p.rate.maximum * income

        return min_(total_copay, max_copay)
