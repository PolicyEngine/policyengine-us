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
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.09",
    )

    def formula(person, period, parameters):
        # SSA state-supplementation cascade (SSA 2011 MD Table 1; COMAR
        # 07.03.07.09): Maryland PAA equals the gap between combined
        # federal+state need and federal SSI plus residual countable
        # income. Per SSA 2011 MD Table 1 footnote a, the individual
        # state-supp rate applies to each member of a couple, so the
        # cascade always uses the federal individual FBR — never
        # couple_FBR/2 — with the $30/mo medical-facility cap for REHAB
        # residents per 42 USC § 1382(e)(1)(A). Federal SSI is its own
        # variable; this formula only computes the state contribution.
        p_ssi = parameters(period).gov.ssa.ssi.amount
        arrangement = person("ssi_federal_living_arrangement", period.this_year)
        is_medical_facility = (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        federal_ssi_max = where(
            is_medical_facility, p_ssi.medical_facility, p_ssi.individual
        )

        combined_need = person("md_paa_total_cost_of_care", period)
        state_supp_max = max_(combined_need - federal_ssi_max, 0)

        countable = person("ssi_countable_income", period)
        income_excess = max_(countable - federal_ssi_max, 0)

        return max_(state_supp_max - income_excess, 0)
