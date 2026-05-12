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
        "https://www.law.cornell.edu/uscode/text/42/1382",
    )

    def formula(person, period, parameters):
        return max_(person("uncapped_ssi", period), 0)
