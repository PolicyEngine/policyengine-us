from policyengine_us.model_api import *


class ssdi_aime(Variable):
    value_type = float
    entity = Person
    label = "SSDI Average Indexed Monthly Earnings (AIME)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ssa.gov/oact/cola/piaformula.html"
    documentation = """
    Average Indexed Monthly Earnings used for SSDI benefit calculation.
    Based on up to 35 highest-earning years of work history, indexed for wage growth.

    Per 42 USC 415(b), AIME requires indexing historical covered earnings to
    national average wage levels. Since PolicyEngine lacks access to lifetime
    earnings records, this is an input variable. Users should provide their
    AIME as calculated by SSA or estimate based on their earnings history.
    """
