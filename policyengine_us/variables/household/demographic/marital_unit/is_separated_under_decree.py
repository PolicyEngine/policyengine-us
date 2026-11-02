from policyengine_us.model_api import *


class is_separated_under_decree(Variable):
    value_type = bool
    entity = Person
    label = "Legally separated under a decree of separate maintenance"
    documentation = """
    Whether the person is legally separated from their spouse under a decree
    of divorce or of separate maintenance. IRC 7703(a)(2) treats such a
    person as not married. A written separation agreement without a decree
    does not count. Defaults to false because survey data cannot tell a
    decree from an informal separation, so is_separated alone keeps the
    married reading.
    """
    definition_period = YEAR
    default_value = False
    reference = "https://www.law.cornell.edu/uscode/text/26/7703#a_2"
