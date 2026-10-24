from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class ut_dws_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Utah DWS State Supplemental Payment"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://jobs.utah.gov/infosource/eligibilitymanual/200_Program_Eligibility_Requirements/205-10_State_Supplemental_Payments_to_SSI_Recipients_-_General_Information.htm",
        "https://jobs.utah.gov/infosource/eligibilitymanual/200_Program_Eligibility_Requirements/205_Financial_Assistance_General_Information.htm",
        "https://jobs.utah.gov/infosource/eligibilitymanual/Obsolete_Policy/Obsolete_200_Program_Eligibility_Requirements/O205/O205-10_%284_1_04_to_12_31_13%29_State_Supp_Payments_SSI_Recipients_Gen_Info.htm",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ut.html",
    )
    documentation = """
    Living alone is read from household membership: a person with no other
    household member who is outside a medical treatment facility and not
    incarcerated lives alone. A resident of a medical facility where Medicaid
    pays half or less of the cost is judged by household membership like
    anyone else. Set receives_ssi when the person reports an SSI payment that
    the model does not compute.
    """

    def formula(person, period, parameters):
        # 205-10: "Customers who are receiving Supplemental Security Income
        # (SSI) or who meet SSI criteria other than income are eligible".
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # is_ssi_eligible applies SSI's aged, blind or disabled, resource and
        # immigration criteria, so an SSI denial on other grounds also denies
        # the supplement ("Individuals who are denied or closed SSI for reasons
        # other than exceeding the income"). Applicants for any financial
        # assistance program must apply for other benefits they may be entitled
        # to (205, "Application for Other Possible Benefits"), so a person whose
        # income would qualify for SSI must take it up.
        # NOTE: The over-income path has no take-up, so in microsimulation it
        # reaches every eligible non-recipient who does not live alone, though
        # 205-10 lets DWS reduce the amounts "to stay within budget".
        over_income_for_ssi = person("is_ssi_eligible", period) & (
            person("uncapped_ssi", period) <= 0
        )
        # Not eligible: "Individuals who live in a public or private
        # institution where Medicaid pays more than 50 percent of their cost of
        # care" and "Individuals who are incarcerated".
        arrangement = person("ssi_federal_living_arrangement", period)
        medicaid_institution = (
            arrangement == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        )
        incarcerated = person("is_incarcerated", period)
        # Not eligible: "Single individuals who live alone." Members living in
        # a medical treatment facility or incarcerated do not share the home.
        # The count leaves out the person themselves, and a spouse at home
        # means the person does not live alone.
        # NOTE: The 2004-2013 edition of 205-10, when SSA paid the supplement,
        # paid "$3.13 for a single person living with others", and SSA's
        # January 2011 table paid individuals only in the household of
        # another (federal code B). The current edition pays "a single person"
        # and excludes only "Single individuals who live alone", so the model
        # also pays a single person living with others in their own household.
        facility = person("ssi_lives_in_medical_treatment_facility", period)
        housemate = ~facility & ~incarcerated
        lives_alone = (person.household.sum(housemate) - housemate) == 0
        return (
            (receives_ssi | over_income_for_ssi)
            & ~medicaid_institution
            & ~incarcerated
            & ~lives_alone
        )
