from policyengine_us.model_api import *


class ca_sf_caap_personal_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets personal property limit for San Francisco County CAAP"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sf.caap.eligibility.personal_property.limit
        # Only liquid cash/savings/checking count toward the Medi-Cal property
        # reserve (Title 22 Section 50420; SEC. 20.7-13). Asset exemptions such
        # as burial funds and life insurance are not tracked at the moment, but
        # spm_unit_cash_assets already excludes them. The motor vehicle rule is
        # modeled separately in ca_sf_caap_vehicle_eligible (Manual 92-26).
        cash_assets = spm_unit("spm_unit_cash_assets", period.this_year)
        budget_unit_size = spm_unit("ca_sf_caap_budget_unit_size", period)
        # The Manual quotes only the 1-person ($2,000) and 2-person ($3,000)
        # reserves; units of 3+ apply the 2-person limit. Title 22 Section 50420
        # scales further for larger units, but we don't track that at the moment.
        limit = where(budget_unit_size >= 2, p.couple, p.single)
        return cash_assets <= limit
