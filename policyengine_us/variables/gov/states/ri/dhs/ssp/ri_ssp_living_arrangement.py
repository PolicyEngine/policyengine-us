from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class RISSPLivingArrangement(Enum):
    # NOTE: R.I. Gen. Laws § 40-6-27(a)(1)(vii) lists a $300 supplement for
    # state-licensed supportive residential-care settings. 218-RICR-20-00-5
    # Section 5.6 and SSA's 2026 payment levels publish no such category, so
    # it is not modeled.
    INDEPENDENT = "Own household"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    RESIDENTIAL_CARE = "State-certified residential care or assisted living"
    MEDICAID_INSTITUTION = "Title XIX facility"
    NONE = "No supplement"


class ri_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Rhode Island SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.RI
    possible_values = RISSPLivingArrangement
    default_value = RISSPLivingArrangement.NONE
    reference = (
        # 218-RICR-20-00-5, Section 5.1.1
        "https://risos-apa-production-public.s3.amazonaws.com/DHS/REG_13426_20260109151518643.pdf#page=1",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415012BOS",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415950BOS",
    )
    documentation = """
    Certified care is an explicit input. Category D applies to adult
    individuals only, so ri_ssp pays a child or a member of an eligible couple
    with this input at the own-household rate. Enter separate individual SSI
    claims when institutional residence ends eligible-couple status; the care
    input itself does not override federal SSI claim or income calculations.
    """

    def formula(person, period, parameters):
        federal = person("ssi_federal_living_arrangement", period)
        return select(
            [
                federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY,
                federal == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
            ],
            [
                RISSPLivingArrangement.MEDICAID_INSTITUTION,
                RISSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=RISSPLivingArrangement.INDEPENDENT,
        )
