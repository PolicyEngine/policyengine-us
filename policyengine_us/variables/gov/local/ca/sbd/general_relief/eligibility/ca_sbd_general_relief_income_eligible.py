from policyengine_us.model_api import *


class ca_sbd_general_relief_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets San Bernardino County General Relief income requirements"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx"

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("ca_sbd_general_relief_countable_income", period)
        grant = spm_unit("ca_sbd_general_relief_maximum_basic_grant", period)
        # NOTE: Chapter A states no explicit boundary; a unit whose countable
        # income exactly equals the maximum basic grant would receive a zero
        # payment, so it is treated as not in need. Countable income is
        # rounded to the cent first so float error in the earned-exemption
        # arithmetic cannot flip the exact-equality boundary either way.
        return np.round(countable_income, 2) < grant
