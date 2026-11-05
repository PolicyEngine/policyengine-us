from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mn.dhs.msa.mn_msa_living_arrangement import (
    MNMSALivingArrangement,
)


class mn_msa_payment_category(Variable):
    value_type = Enum
    entity = Person
    label = "Minnesota Supplemental Aid payment category"
    definition_period = MONTH
    defined_for = StateCode.MN
    possible_values = MNMSALivingArrangement
    default_value = MNMSALivingArrangement.INDIVIDUAL_LIVING_ALONE
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44#stat.256D.44.2",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )

    def formula(person, period, parameters):
        # Recipients in Medicaid-financed institutional care are paid under
        # the FLA-D personal-needs cap regardless of reported arrangement.
        # Minn. Stat. 256D.44 subd. 2 gives the living-alone standard to a
        # person eligible for the housing allowance, eligible for a medical
        # assistance home and community-based services waiver, or with the
        # local agency's placement determination under 256I.04 subd. 1a.
        # Neither of the last two requires living in a Housing Support
        # setting.
        federal_arrangement = person("ssi_federal_living_arrangement", period)
        federal_values = federal_arrangement.possible_values
        in_medicaid_facility = person("is_in_medicaid_facility", period.this_year) | (
            federal_arrangement == federal_values.MEDICAL_TREATMENT_FACILITY
        )
        living_arrangement = person("mn_msa_living_arrangement", period)
        LA = MNMSALivingArrangement
        living_alone_pathway = (
            person("mn_msa_housing_assistance_eligible", period)
            | person("mn_msa_hcbs_waiver_eligible", period)
            | person("mn_msa_housing_support_plan_approved", period)
        )
        is_couple = (living_arrangement == LA.COUPLE_LIVING_ALONE) | (
            living_arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        apply_housing_standard = where(
            is_couple,
            person.marital_unit.any(living_alone_pathway),
            living_alone_pathway,
        )
        housing_standard_arrangement = select(
            [
                living_arrangement == LA.INDIVIDUAL_LIVING_WITH_OTHERS,
                living_arrangement == LA.COUPLE_LIVING_WITH_OTHERS,
            ],
            [
                LA.INDIVIDUAL_LIVING_ALONE,
                LA.COUPLE_LIVING_ALONE,
            ],
            default=living_arrangement,
        )
        community_arrangement = where(
            apply_housing_standard,
            housing_standard_arrangement,
            living_arrangement,
        )
        return where(
            in_medicaid_facility,
            LA.MEDICAID_FACILITY,
            community_arrangement,
        )
