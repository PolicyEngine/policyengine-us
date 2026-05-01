from policyengine_us.model_api import *


class MNMSALivingArrangement(Enum):
    INDIVIDUAL_LIVING_ALONE = "Individual living alone"
    INDIVIDUAL_LIVING_WITH_OTHERS = "Individual living with others"
    COUPLE_LIVING_ALONE = "Couple living alone"
    COUPLE_LIVING_WITH_OTHERS = "Couple living with others"
    MEDICAID_FACILITY = "Medicaid facility"
    NONE = "Not in a qualifying arrangement"


class mn_msa_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Minnesota Supplemental Aid living arrangement"
    definition_period = MONTH
    defined_for = StateCode.MN
    possible_values = MNMSALivingArrangement
    default_value = MNMSALivingArrangement.INDIVIDUAL_LIVING_ALONE
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=6",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 2 and Combined Manual 0020.21,
        # the MSA assistance standard is keyed off of whether the recipient
        # is a single person or part of a married couple (both eligible)
        # and whether they live alone or share a household with others.
        # Recipients of HCBS waivers, GRH plans, or MSA Housing Assistance
        # are treated as living alone regardless of cohabitation.
        federal_arrangement = person("ssi_federal_living_arrangement", period.this_year)
        FED = federal_arrangement.possible_values
        in_medicaid_facility = person("is_in_medicaid_facility", period.this_year) | (
            federal_arrangement == FED.MEDICAL_TREATMENT_FACILITY
        )

        # Couple gating: both spouses categorically eligible (ABD), joint
        # claim. Avoids circular dependency through the MSA→SSI computation
        # by using is_ssi_aged_blind_disabled rather than mn_msa_eligible_person.
        categorically_eligible = person("mn_msa_categorically_eligible", period)
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        both_eligible = (
            person.marital_unit.sum(categorically_eligible) == 2
        ) & joint_claim

        treated_as_living_alone = person("mn_msa_treated_as_living_alone", period)
        lives_with_others = (
            person("mn_msa_lives_with_others", period) & ~treated_as_living_alone
        )

        LA = MNMSALivingArrangement
        couple_alone = both_eligible & ~lives_with_others
        couple_with_others = both_eligible & lives_with_others
        individual_with_others = (
            categorically_eligible & ~both_eligible & lives_with_others
        )
        individual_alone = categorically_eligible & ~both_eligible & ~lives_with_others

        return select(
            [
                ~categorically_eligible,
                in_medicaid_facility,
                couple_alone,
                couple_with_others,
                individual_with_others,
                individual_alone,
            ],
            [
                LA.NONE,
                LA.MEDICAID_FACILITY,
                LA.COUPLE_LIVING_ALONE,
                LA.COUPLE_LIVING_WITH_OTHERS,
                LA.INDIVIDUAL_LIVING_WITH_OTHERS,
                LA.INDIVIDUAL_LIVING_ALONE,
            ],
            default=LA.NONE,
        )
