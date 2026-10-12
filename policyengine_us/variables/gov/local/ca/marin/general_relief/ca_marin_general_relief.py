from policyengine_us.model_api import *


class ca_marin_general_relief(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Marin County General Relief"
    definition_period = MONTH
    defined_for = "ca_marin_general_relief_eligible"
    reference = (
        "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=17",
        "https://hhs.marincounty.gov/services/get-cash-assistance-myself-general-relief/general-relief-cash-assistance",
    )

    def formula(spm_unit, period, parameters):
        grant = spm_unit("ca_marin_general_relief_max_grant", period)
        # Net income is YEAR-defined; reading it at the monthly period
        # auto-divides the annual figure to a monthly amount.
        net_income = spm_unit("ca_marin_general_relief_net_income", period)
        return max_(grant - net_income, 0)
