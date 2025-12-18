from policyengine_us.model_api import *


class msp_fpg(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "MSP Federal Poverty Guideline"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d#p",
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
    )
    documentation = """
    The Federal Poverty Guideline used for MSP eligibility is based on
    individual or couple status, not the full household/SPM unit size.
    Per 42 U.S.C. 1396d(p), MSP income limits are based on the federal
    poverty line for a family of the size involved.

    Note: Published Medicare.gov limits are $20/month higher than raw FPL
    because they include the $20 general income exclusion in the threshold.
    Our implementation applies the $20 exclusion to income instead, which
    is mathematically equivalent: (income - $20) <= FPL == income <= (FPL + $20)
    """

    def formula(person, period, parameters):
        # MSP uses individual (1 person) or couple (2 persons) FPG,
        # not the full SPM unit size.
        # Note: These are raw FPL values. Published limits are $20 higher
        # because we apply the $20 exclusion to income (msp_countable_income)
        # rather than adding it to the threshold.
        married = person.spm_unit("spm_unit_is_married", period)
        state_group = person.household("state_group_str", period)
        p = parameters(period).gov.hhs.fpg
        p1 = p.first_person[state_group]
        pn = p.additional_person[state_group]
        # 1 person if single, 2 persons if married
        individual_fpg = p1
        couple_fpg = p1 + pn
        return where(married, couple_fpg, individual_fpg)
