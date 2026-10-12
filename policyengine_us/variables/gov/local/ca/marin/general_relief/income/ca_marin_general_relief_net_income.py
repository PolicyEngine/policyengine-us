from policyengine_us.model_api import *


class ca_marin_general_relief_net_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = (
        "Net income under the Marin County General Relief after mandatory deductions"
    )
    definition_period = YEAR
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=11"

    def formula(spm_unit, period, parameters):
        gross_income = add(spm_unit, period, ["ca_marin_general_relief_gross_income"])
        # The Standards allow only mandatory deductions (income tax, Social
        # Security, Medicare, State Disability/Unemployment Insurance). We use
        # paycheck withholdings (FICA + income tax) as the proxy; we do not
        # subtract SDI/UI employee contributions at the moment.
        paycheck_withholdings = spm_unit("spm_unit_paycheck_withholdings", period)
        return max_(gross_income - paycheck_withholdings, 0)
