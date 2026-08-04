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
        "https://www.law.cornell.edu/uscode/text/42/1382#e_1_A",
    )

    def formula(person, period, parameters):
        amount = person("ssi_amount_if_eligible", period)
        countable_income = person("md_paa_countable_income", period)
        return max_(amount - countable_income, 0)
