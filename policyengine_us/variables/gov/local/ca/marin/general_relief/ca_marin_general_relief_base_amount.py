from policyengine_us.model_api import *


class ca_marin_general_relief_base_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Marin County General Relief base amount"
    definition_period = MONTH
    defined_for = "ca_marin_general_relief_eligible"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=17"

    def formula(spm_unit, period, parameters):
        grant = spm_unit("ca_marin_general_relief_max_grant", period)
        # Net income is YEAR-defined; divide to a monthly figure to subtract
        # from the monthly grant.
        net_income = add(
            spm_unit, period.this_year, ["ca_marin_general_relief_net_income"]
        )
        monthly_net_income = net_income / MONTHS_IN_YEAR
        return max_(grant - monthly_net_income, 0)
