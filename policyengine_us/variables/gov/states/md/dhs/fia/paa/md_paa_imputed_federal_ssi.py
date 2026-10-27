from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class md_paa_imputed_federal_ssi(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA imputed federal SSI"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.03",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.09",
        "https://www.law.cornell.edu/uscode/text/42/1382#e_1_A",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
    )

    def formula(person, period, parameters):
        amount = person("ssi_amount_if_eligible", period)
        countable_income = person("md_paa_countable_income", period)
        imputed_ssi = max_(amount - countable_income, 0)
        # SSA cannot pay SSI to people who fail its citizen or
        # qualified-noncitizen test, so there is no federal SSI to impute.
        # PAA then pays allowable needs less net countable income
        # (COMAR 07.03.07.09A).
        immigration_status = person("immigration_status", period.this_year)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        is_qualified_noncitizen = person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        meets_ssi_immigration_test = is_citizen | is_qualified_noncitizen
        # A person who reports SSI receipt although they fail the model's test
        # (for example one SSA pays under 8 U.S.C. 1612(a)(2)(E), which the
        # model does not encode) gets the SSI SSA pays. PAA counts only their
        # own income, so impute the individual rate for the living arrangement
        # less that income, and under spouse deeming the lesser of that and
        # the couple rate less own and deemed income (20 CFR 416.1163(d)-(e);
        # POMS SI 01320.430).
        p = parameters(period).gov.ssa.ssi.amount
        arrangement = person("ssi_federal_living_arrangement", period)
        arrangements = SSIFederalLivingArrangement
        in_medical_facility = arrangement == arrangements.MEDICAL_TREATMENT_FACILITY
        individual_rate = select(
            [
                in_medical_facility,
                arrangement == arrangements.ANOTHER_PERSONS_HOUSEHOLD,
            ],
            [p.medical_facility, p.individual * (1 - p.one_third_reduction_rate)],
            default=p.individual,
        )
        individual_ssi = individual_rate - countable_income
        deemed_income = person("ssi_income_deemed_from_ineligible_spouse", period)
        couple_ssi = p.couple - (countable_income + deemed_income)
        deeming = (
            person("is_ssi_spousal_deeming_applies", period.this_year)
            & ~in_medical_facility
        )
        reported_ssi = max_(
            where(deeming, min_(couple_ssi, individual_ssi), individual_ssi), 0
        )
        reports_ssi = person("receives_ssi", period)
        return select(
            [meets_ssi_immigration_test, reports_ssi],
            [imputed_ssi, reported_ssi],
            default=0,
        )
