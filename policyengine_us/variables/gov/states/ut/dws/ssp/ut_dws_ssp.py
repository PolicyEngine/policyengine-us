from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ut_dws_ssp(Variable):
    value_type = float
    entity = Person
    label = "Utah DWS State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    defined_for = "ut_dws_ssp_eligible"
    # The Department of Workforce Services pays this supplement "on a
    # quarterly basis following the end of the quarter" (205-10). The model
    # reports the monthly amount in the month it accrues.
    reference = (
        "https://jobs.utah.gov/infosource/eligibilitymanual/200_Program_Eligibility_Requirements/205-10_State_Supplemental_Payments_to_SSI_Recipients_-_General_Information.htm",
        # Statutory basis: Appropriation Act for the Department of Workforce
        # Services.
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ut.html",
    )
    documentation = """
    Spouses are the members of a marital unit. Set
    ssi_lives_in_another_persons_household,
    ssi_receives_shelter_from_others_in_household and ssi_others_pay_all_meals
    for both spouses to place a couple in the household of another.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dws.ssp.amount
        # The couple amounts apply when both spouses qualify, and each spouse
        # receives half. A person whose spouse does not qualify receives the
        # single person amount.
        eligible = person("ut_dws_ssp_eligible", period)
        couple = person.marital_unit.sum(eligible) == 2
        # 205-10 pays couples "who live in the household of another" and
        # couples "who live alone or with others in their own household". SSA
        # paid the same rows by federal living arrangement codes B and A
        # (205-10, 2004-2013 edition; SSA's January 2011 table).
        arrangement = person("ssi_federal_living_arrangement", period)
        another_household = (
            arrangement == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD
        )
        couple_amount = where(
            another_household, p.couple.another_household, p.couple.own_household
        )
        return where(couple, couple_amount / 2, p.individual)
