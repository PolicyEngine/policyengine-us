from policyengine_us.model_api import *


class mn_mfip_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_001809"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 142G.16, Subd. 1(b)(2):
        # Deduct actual dependent care up to $200/child under 2, $175/child 2+.
        # Only applies to eligibility test, not benefit calculation.
        # Per Combined Manual 0018.09, the deduction also covers care of a
        # disabled adult in the unit; the manual states no separate adult
        # cap, so we apply the $175 age-two-or-older tier.
        p = parameters(period).gov.states.mn.dcyf.mfip.income.deductions.dependent_care
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        disabled_adult = person("is_adult", period.this_year) & person(
            "is_disabled", period.this_year
        )
        age = person("monthly_age", period)
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        care_recipient = dependent | disabled_adult
        max_deduction_per_person = p.calc(age) * care_recipient
        total_max_deduction = spm_unit.sum(max_deduction_per_person)
        return min_(childcare_expenses + adult_care_expenses, total_max_deduction)
