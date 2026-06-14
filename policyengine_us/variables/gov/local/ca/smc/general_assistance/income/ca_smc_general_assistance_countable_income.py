from policyengine_us.model_api import *


class ca_smc_general_assistance_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Mateo County General Assistance countable income"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = (
        "https://www.smcgov.org/media/153295/download?inline=#page=2",
        "https://sanmateocounty.legistar.com/View.ashx?GUID=25359405-C9EB-4566-AE97-D927CC455B02&ID=9802358&M=F#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.smc.general_assistance.income
        total = add(spm_unit, period, p.sources)
        earned = add(spm_unit, period, p.earned_sources)
        deduction = max_(earned, 0) * p.earned_income_deduction_rate
        return total - deduction
