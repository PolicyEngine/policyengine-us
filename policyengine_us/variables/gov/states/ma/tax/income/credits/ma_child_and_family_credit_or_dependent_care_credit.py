from policyengine_us.model_api import *


class ma_child_and_family_credit_or_dependent_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA dependent or dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/mass-general-laws-c62-ss-6"  # (x-y)
    )
    defined_for = StateCode.MA
    documentation = "The CFTC replaces the Dependent Care Tax Credit and the Household Dependent Tax Credit with Child and Family Tax Credit for tax years beginning on or after January 1, 2023."

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.credits.dependent_care
        # MA taxpayers can only take either the dependent credit or the
        # dependent care credit.
        dependent_credit = tax_unit("ma_child_and_family_credit", period)
        if p.in_effect:
            return max_(
                dependent_credit,
                tax_unit("ma_dependent_care_credit", period),
            )
        return dependent_credit
