from policyengine_us.model_api import *


class la_fitap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Louisiana FITAP"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/louisiana/La-Admin-Code-tit-67-SS-III-1229"
    defined_for = "la_fitap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.dcfs.fitap
        flat_grant = spm_unit("la_fitap_flat_grant", period)
        countable_income = spm_unit("la_fitap_countable_income", period)

        # DCFS manual B-641-1-FITAP: the deficit between the flat grant and
        # countable income, rounded down. If the rounded deficit is $10 or
        # more it is the grant amount; if it is less than $10 the unit is
        # FITAP-eligible but no grant is paid.
        deficit = max_(flat_grant - countable_income, 0)
        rounded_deficit = np.floor(deficit)
        grant = min_(rounded_deficit, flat_grant)
        return where(grant >= p.minimum_payment, grant, 0)
