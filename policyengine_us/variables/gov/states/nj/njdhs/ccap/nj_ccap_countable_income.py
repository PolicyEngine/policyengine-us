from policyengine_us.model_api import *


class nj_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NJ
    reference = "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=23"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap.income.countable_income
        # N.J.A.C. 10:15 does not enumerate an explicit minor-child earnings
        # exclusion the way VA (8VAC20-790-40(H)) and CT (17b-749-05(b)(2)(E))
        # do. However, the NJ CCAP application form (CC-1, 03/24) Section D
        # collects wage and self-employment income only for the applicant and
        # co-applicant; there is no field for minor children's earnings. We
        # therefore operationalize the NJ rule by summing earned income
        # sources only for tax-unit heads and spouses (i.e. the applicant
        # and co-applicant) and summing unearned income across all members,
        # matching how the application form treats household income.
        person = spm_unit.members
        # `age` / `is_tax_unit_head_or_spouse` are YEAR-defined; use
        # period.this_year to read the annual value in a monthly formula.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        earned_per_person = sum(person(source, period) for source in p.earned_sources)
        applicant_earned_income = spm_unit.sum(earned_per_person * is_head_or_spouse)
        unearned_income = add(spm_unit, period, p.unearned_sources)
        return applicant_earned_income + unearned_income
