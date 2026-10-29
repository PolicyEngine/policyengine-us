from policyengine_us.model_api import *


class dc_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "DC Temporary Assistance for Needy Families (TANF) countable unearned income"
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11"  # (a)(8)
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.tanf.income
        total_unearned_income = add(spm_unit, period, ["dc_tanf_gross_unearned_income"])
        # dc_tanf_countable_income removes a GAC child's gross unearned income,
        # child support included, so only TANF members' child support is
        # disregarded here.
        person = spm_unit.members
        tanf_member = ~person("dc_gac_eligible_child", period)
        child_support = spm_unit.sum(
            add(person, period, ["child_support_received"]) * tanf_member
        )
        child_support_deduction = min_(child_support, p.deductions.child_support)

        return max_(0, total_unearned_income - child_support_deduction)
