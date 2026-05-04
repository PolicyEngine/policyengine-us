from policyengine_us.model_api import *


class md_paa(Variable):
    value_type = float
    entity = Person
    label = "Maryland Public Assistance to Adults"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/md.html",
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-09",
    )

    def formula(person, period, parameters):
        # SSA state-supplementation cascade (SSA 2011 MD report, Table 1;
        # COMAR 07.03.07.09): Maryland PAA equals the gap between the
        # combined federal+state payment level and what federal SSI plus
        # other countable income provide. State supplementation only —
        # federal SSI is its own variable. REHAB residents are
        # automatically capped at the $30 medical-facility federal SSI
        # rate because md_paa_eligible requires the caller to set
        # `ssi_lives_in_medical_treatment_facility` for them.
        combined_need = person("md_paa_total_cost_of_care", period)
        federal_ssi_max = person("ssi_amount_if_eligible", period)

        # State supplement maximum: the gap federal SSI cannot fill.
        state_supp_max = max_(combined_need - federal_ssi_max, 0)

        # Countable income left after federal SSI is reduced to zero.
        countable = person("ssi_countable_income", period)
        income_excess = max_(countable - federal_ssi_max, 0)

        return max_(state_supp_max - income_excess, 0)
