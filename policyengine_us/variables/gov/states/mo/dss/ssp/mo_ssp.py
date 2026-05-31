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
        "https://revisor.mo.gov/main/OneSection.aspx?section=209.040",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-130",
        "https://dssmanuals.mo.gov/supplemental-aid-to-the-blind/0415-000-00/0415-005-00/",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mo.html",
    )

    def formula(person, period, parameters):
        # We don't model the earned-income-limit-based "most beneficial of two
        # methods" Supplemental Aid to the Blind pathway from DSS Manual
        # 0715.010.10 at the moment; it only applies to the closed
        # 1973-conversion cohort.
        p = parameters(period).gov.states.mo.dss.ssp
        federal_ssi = person("ssi", period)
        sab_remainder = max_(p.sab.maximum_payment - federal_ssi, 0)
        sab_grant = where(
            (sab_remainder > 0) & (sab_remainder < 1),
            1,
            np.floor(sab_remainder + 0.5),
        )
        living_arrangement = person("mo_ssp_living_arrangement", period)
        categories = living_arrangement.possible_values
        snc = p.snc.max_grant
        snc_max_grant = select(
            [
                living_arrangement == categories.RCF_LEVEL_I,
                (living_arrangement == categories.RCF_LEVEL_II_OR_ALF)
                | (living_arrangement == categories.INTERMEDIATE_OR_SKILLED_NO_LOC),
                living_arrangement == categories.SNF_OR_ICF_NON_MEDICAID,
            ],
            [
                snc.rcf_level_i,
                snc.rcf_level_ii_or_alf,
                snc.snf_or_icf_non_medicaid,
            ],
            default=0,
        )
        facility_base_charge = person("mo_snc_facility_base_charge", period)
        countable_income = person("mo_snc_countable_income", period)
        snc_grant = min_(
            max_(facility_base_charge - countable_income, 0),
            snc_max_grant,
        )
        base = where(living_arrangement == categories.SAB, sab_grant, snc_grant)
        return base + person("mo_ssp_personal_needs_allowance", period)
