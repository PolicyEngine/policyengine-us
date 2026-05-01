from policyengine_us.model_api import *


class mn_msa_housing_assistance(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid housing allowance under § 256D.44 Subd. 5(g)"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&dDocName=cm_002324&RevisionSelectionMethod=LatestReleased",
    )

    def formula(person, period, parameters):
        # Minn. Stat. § 256D.44 Subd. 5(g) authorizes a single housing
        # allowance equal to one-half of the federal SSI individual
        # benefit rate. Recipients qualify via either pathway:
        #   (1) Subd. 5(g)(1): institution-relocation, HCBS-waiver
        #       eligible, or shelter cost > 40% of income (formerly
        #       modeled as the Shelter Need allowance).
        #   (2) CM 0023.24: chronic homelessness / housing
        #       stabilization (the original MSA Housing Assistance).
        # The amount is the same (1/2 x FBR) regardless of pathway.
        p = parameters(period).gov.states.mn.dhs.msa.housing_assistance
        ssi_fbr = parameters(period).gov.ssa.ssi.amount.individual
        eligible = person("mn_msa_housing_assistance_eligible", period)
        return eligible * ssi_fbr * p.fbr_multiplier
