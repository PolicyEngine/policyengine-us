from policyengine_us.model_api import *


class mn_msa_special_needs_total(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid total special-needs allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )

    def formula(person, period, parameters):
        # Representative-payee and guardian fees stack with all other
        # special-needs items. The shelter-need allowance (Minn. Stat.
        # § 256D.44 Subd. 5(g)) and MSA Housing Assistance (Combined
        # Manual 0023.24) are mutually exclusive — they serve different
        # housing situations and a recipient cannot receive both for the
        # same arrangement. When both eligibility flags are set, MSA
        # Housing Assistance takes precedence as the stricter program.
        rep_payee_fee = person("mn_msa_representative_payee_fee", period)
        guardian_fee = person("mn_msa_guardian_fee", period)
        shelter_need = person("mn_msa_shelter_need_allowance", period)
        housing_assistance = person("mn_msa_housing_assistance", period)
        housing_aid = where(housing_assistance > 0, housing_assistance, shelter_need)
        return rep_payee_fee + guardian_fee + housing_aid
