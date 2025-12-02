from policyengine_us.model_api import *


class ss_pia(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Primary Insurance Amount (PIA)"
    documentation = "Primary Insurance Amount for Social Security benefits"
    unit = USD
    reference = (
        "https://www.ssa.gov/OACT/COLA/piaformula.html",
        "https://www.law.cornell.edu/uscode/text/42/415#a_1",
    )

    def formula(person, period, parameters):
        aime = person("ss_aime", period)

        p = parameters(period).gov.ssa.social_security.pia

        # Calculate PIA using the marginal rate scale
        pia = p.formula_factors.calc(aime)

        # SSA rounds down to nearest 10 cents (dime)
        # Source: https://www.ssa.gov/OACT/ProgData/retirebenefit1.html
        return np.floor(pia * 10) / 10
