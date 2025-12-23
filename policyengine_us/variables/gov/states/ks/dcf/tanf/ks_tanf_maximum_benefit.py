from policyengine_us.model_api import *


class ks_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF maximum benefit amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-101",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-100 and K.A.R. 30-4-101:
        # Payment standard = Basic allowance + Shelter allowance
        # Using High Population Counties (Group III) rates for Non-shared Living
        # Group III shelter = $109/month
        # Counties: Butler, Jefferson, Leavenworth, McPherson, Miami, Osage,
        #           Reno, Rice, Riley, Sedgwick, Shawnee, Wyandotte
        p = parameters(period).gov.states.ks.dcf.tanf.payment_standard
        max_size_in_table = parameters(
            period
        ).gov.states.ks.dcf.tanf.max_family_size_in_table
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, max_size_in_table)
        base_amount = p.amount[capped_size]
        additional_people = max_(unit_size - max_size_in_table, 0)
        additional_amount = additional_people * p.additional_person_amount
        return base_amount + additional_amount
