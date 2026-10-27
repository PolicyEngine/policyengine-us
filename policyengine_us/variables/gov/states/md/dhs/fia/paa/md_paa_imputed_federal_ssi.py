from policyengine_us.model_api import *


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
    )

    def formula(person, period, parameters):
        amount = person("ssi_amount_if_eligible", period)
        countable_income = person("md_paa_countable_income", period)
        imputed_ssi = max_(amount - countable_income, 0)
        # SSA cannot pay SSI to people who fail its citizen or
        # qualified-noncitizen test, so there is no federal SSI to impute.
        # PAA then pays allowable needs less net countable income
        # (COMAR 07.03.07.09A). A person who reports SSI receipt, for example
        # one SSA pays under an exception the model does not encode such as
        # 8 U.S.C. 1612(a)(2)(E), keeps the imputed SSI. The repository's SSI
        # receipt convention is (ssi > 0) | receives_ssi, and ssi > 0 already
        # implies the citizen or qualified-noncitizen test.
        immigration_status = person("immigration_status", period.this_year)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        is_qualified_noncitizen = person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        reports_ssi = person("receives_ssi", period)
        not_barred_from_ssi = is_citizen | is_qualified_noncitizen | reports_ssi
        return where(not_barred_from_ssi, imputed_ssi, 0)
