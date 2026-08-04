from policyengine_us.model_api import *


class ca_marin_general_relief_personal_property_limit(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    label = "Limit for the Marin County General Relief personal property requirements"
    defined_for = "in_marin"
    reference = (
        "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=11",
        "https://hhs.marincounty.gov/services/get-cash-assistance-myself-general-relief/general-relief-cash-assistance",
    )

    def formula(spm_unit, period, parameters):
        # Month-defined to match the rest of the GR eligibility chain (the limit
        # is a single era with no mid-year change). spm_unit_is_married is
        # year-defined, so read it with period.this_year.
        married = spm_unit("spm_unit_is_married", period.this_year)
        p = parameters(
            period
        ).gov.local.ca.marin.general_relief.eligibility.limit.personal_property
        return where(married, p.married, p.single)
