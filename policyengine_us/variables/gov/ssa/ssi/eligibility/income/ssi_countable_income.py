from policyengine_us.model_api import *


class ssi_countable_income(Variable):
    value_type = float
    entity = Person
    label = "SSI countable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382a#b"
    documentation = """
    Calculates total countable income for SSI:
      - Earned (after ignoring blind/disabled student exclusion)
      - Unearned
      - Parental deemed if child
      - Spousal deemed if married to an ineligible spouse
      - In-kind support and maintenance (ISM) via the PMV rule for Status A
      - Applies standard SSI exclusions ($20 general, $65 earned, 50% earned).

    ISM is added to unearned income BEFORE exclusions per 20 CFR § 416.1140.
    The PMV formula includes $20 so that after the general exclusion applies,
    the net countable ISM equals 1/3 FBR (matching POMS SI 00835.901 values).
    """

    def formula(person, period, parameters):
        # Sum completed monthly budgets; supplied amounts retain their annual basis.
        return person("ssi_countable_income_monthly", period)
