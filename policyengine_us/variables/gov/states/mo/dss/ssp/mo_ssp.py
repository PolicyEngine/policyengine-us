from policyengine_us.model_api import *


class mo_ssp(Variable):
    value_type = float
    entity = Person
    label = "Missouri State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = "mo_ssp_eligible"
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/07/mhabd-appendix-j.pdf#page=2",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mo.html",
    )

    def formula(person, period, parameters):
        # We don't model the earned-income-limit-based "most beneficial of two
        # methods" Supplemental Aid to the Blind pathway from DSS Manual
        # 0715.010.10 at the moment; it only applies to the closed
        # 1973-conversion cohort.
        p = parameters(period).gov.states.mo.dss.ssp
        federal_ssi = person("ssi", period)
        sab_grant = min_(
            max_(p.sab.consolidated_standard - federal_ssi, 0),
            p.sab.max_grant_cap,
        )
        living_arrangement = person("mo_ssp_living_arrangement", period)
        categories = living_arrangement.possible_values
        snc = p.snc.max_grant
        base = select(
            [
                living_arrangement == categories.SAB,
                living_arrangement == categories.RCF_LEVEL_I,
                (living_arrangement == categories.RCF_LEVEL_II_OR_ALF)
                | (living_arrangement == categories.INTERMEDIATE_OR_SKILLED_NO_LOC),
                living_arrangement == categories.SNF_OR_ICF_NON_MEDICAID,
            ],
            [
                sab_grant,
                snc.rcf_level_i,
                snc.rcf_level_ii_or_alf,
                snc.snf_or_icf_non_medicaid,
            ],
            default=0,
        )
        return base + person("mo_ssp_personal_needs_allowance", period)
