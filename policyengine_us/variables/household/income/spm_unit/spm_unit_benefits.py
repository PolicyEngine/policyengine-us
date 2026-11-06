from policyengine_us.model_api import *


class spm_unit_benefits(Variable):
    value_type = float
    entity = SPMUnit
    label = "Benefits"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        p = parameters(period)
        # A reform that pays a new benefit adds it to this parameter rather
        # than redefining this variable, so it counts every baseline program.
        benefits = list(p.gov.household.spm_unit_benefits)
        if p.gov.contrib.ubi_center.flat_tax.deduct_ptc:
            benefits.append("assigned_aca_ptc")
        # The SPM's capped value of housing assistance. It stays out of the
        # parameter so that no other aggregate can read an SPM valuation cap.
        if not p.gov.hud.abolition:
            benefits.append("spm_unit_capped_housing_subsidy")
        return add(spm_unit, period, benefits)
