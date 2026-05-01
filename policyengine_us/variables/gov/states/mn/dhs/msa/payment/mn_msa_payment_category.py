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
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )

    def formula(person, period, parameters):
        # Per Minn. Stat. § 256D.44 Subd. 2 and Combined Manual 0020.21,
        # recipients receiving Medicaid-financed institutional care are paid
        # under the FLA-D personal-needs cap regardless of their otherwise
        # reported MSA living arrangement.
        federal_arrangement = person("ssi_federal_living_arrangement", period.this_year)
        federal_values = federal_arrangement.possible_values
        in_medicaid_facility = person("is_in_medicaid_facility", period.this_year) | (
            federal_arrangement == federal_values.MEDICAL_TREATMENT_FACILITY
        )
        living_arrangement = person("mn_msa_living_arrangement", period)
        return where(
            in_medicaid_facility,
            MNMSALivingArrangement.MEDICAID_FACILITY,
            living_arrangement,
        )
