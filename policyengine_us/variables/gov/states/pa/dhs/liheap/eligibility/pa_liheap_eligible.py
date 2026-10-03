from policyengine_us.model_api import *


class pa_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Pennsylvania LIHEAP eligibility"
    defined_for = StateCode.PA
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=38",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=35",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("pa_liheap_household_size", period)
        income = spm_unit("pa_liheap_income", period)
        limit = spm_unit("pa_liheap_income_limit", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # Housing-assistance flags approximate income-based rent. An explicit
        # primary heating obligation can qualify subsidized heat-in-rent tenants;
        # a secondary-fuel bill alone does not establish that obligation.
        responsible = spm_unit("has_heating_expense", period) | (
            heat_in_rent & ~subsidized
        )
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        # No asset test or categorical receipt bypass. Institutional residence,
        # prior awards, legal fixtures, and agency-paid bills need facts not
        # fully identified by current inputs. Expense does not cap eligibility.
        return (
            (size > 0) & (income <= limit) & responsible & (heating_type != fuel.NONE)
        )
