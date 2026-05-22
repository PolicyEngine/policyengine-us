from policyengine_us.model_api import *


class AKSSPLivingArrangement(Enum):
    INDEPENDENT = "Living independently"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    ASSISTED_LIVING = "Assisted living home"
    MEDICAID_FACILITY = "Medicaid facility"


class ak_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Alaska Adult Public Assistance living arrangement"
    definition_period = YEAR
    defined_for = StateCode.AK
    possible_values = AKSSPLivingArrangement
    default_value = AKSSPLivingArrangement.INDEPENDENT
    reference = (
        "https://health.alaska.gov/en/services/adult-public-assistance-apa/",
        "http://dpaweb.hss.state.ak.us/POLICY/PDF/APA-Standards.pdf",
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=830",
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=833",
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=834",
        "https://health.alaska.gov/en/services/assisted-living-licensing-and-renewals/",
        "https://www.akleg.gov/statutesPDF/Title-47.pdf#page=310",
        "https://www.law.cornell.edu/cfr/text/20/416.1132",
        "https://www.law.cornell.edu/cfr/text/20/416.414",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ak.pdf#page=2",
    )

    def formula(person, period):
        arrangement = person("ssi_federal_living_arrangement", period)
        in_medical_facility = (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        in_another_household = (
            arrangement == arrangement.possible_values.ANOTHER_PERSONS_HOUSEHOLD
        )

        in_assisted_living = person("ak_resides_in_assisted_living_home", period)

        return select(
            [in_medical_facility, in_assisted_living, in_another_household],
            [
                AKSSPLivingArrangement.MEDICAID_FACILITY,
                AKSSPLivingArrangement.ASSISTED_LIVING,
                AKSSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=AKSSPLivingArrangement.INDEPENDENT,
        )
