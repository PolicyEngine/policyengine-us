from policyengine_us.model_api import *


class mo_tanf_earned_income_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF earned income deductions for Percentage of Need test"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30-10/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30-20/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # 13 CSR 40-2.310(9)(A) and (9)(D): the disregards apply to each
        # participant's earned income separately, then the per-person
        # amounts are summed (DSS Manual 0210.015.30.10: "Add together
        # the $30 plus 1/3 disregard amount from each person's income").
        # The membership and exemption masks must stay identical to
        # mo_tanf_gross_earned_income so deductions attach only to
        # earnings that are counted: a loss earner's negative deduction
        # then cancels exactly against their negative gross in
        # mo_tanf_countable_income. Diverging the masks (or flooring one
        # side alone) breaks that cancellation.
        person = spm_unit.members
        member = person("mo_tanf_is_assistance_unit_member", period)
        exempt = person("is_mo_tanf_earned_income_exempt", period)
        person_deductions = person("mo_tanf_earned_income_deductions_person", period)
        child_care = spm_unit("mo_tanf_child_care_deduction", period)
        return spm_unit.sum(person_deductions * member * ~exempt) + child_care
