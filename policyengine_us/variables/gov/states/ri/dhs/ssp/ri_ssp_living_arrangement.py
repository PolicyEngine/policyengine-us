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
    Certified care comes from ri_ssp_certified_residential_care. Category D
    applies to adult individuals only, so ri_ssp pays a child or a member of an
    eligible couple with certified care at the own-household rate. When
    institutional residence ends eligible-couple status, set ssi_claim_is_joint
    (a yearly formula variable) to false for both spouses; an input replaces the
    formula for everyone in the simulation, so set it to true for any other
    joint couple. Certified care itself does not override federal SSI claim or
    income calculations. Certified residents are in federal living arrangement
    A (POMS SI BOS01415.012 B.1), so do not also set the household-of-another
    SSI inputs for them.
    """

    def formula(person, period, parameters):
        federal = person("ssi_federal_living_arrangement", period)
        # Category D is used with federal living arrangement A only (POMS SI
        # BOS01415.012 B.1), so a Title XIX facility resident is Category E.
        # Certified residents are in federal arrangement A, so certified care
        # precedes the household of another.
        return select(
            [
                federal == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY,
                person("ri_ssp_certified_residential_care", period),
                federal == SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
            ],
            [
                RISSPLivingArrangement.MEDICAID_INSTITUTION,
                RISSPLivingArrangement.RESIDENTIAL_CARE,
                RISSPLivingArrangement.HOUSEHOLD_OF_ANOTHER,
            ],
            default=RISSPLivingArrangement.INDEPENDENT,
        )
