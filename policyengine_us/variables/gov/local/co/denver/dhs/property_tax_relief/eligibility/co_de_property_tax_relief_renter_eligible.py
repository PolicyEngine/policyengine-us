from policyengine_us.model_api import *


class co_de_property_tax_relief_renter_eligible(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Eligible for the renter Denver Property Tax Relief"
    definition_period = YEAR
    reference = "https://denvergov.org/files/content/public/v/37/government/agencies-departments-offices/agencies-departments-offices-directory/denver-human-services/be-supported/additional-assistance/property-tax-relief/denver-property-tax-relief-program-year-2021-rules.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.co.denver.dhs.property_tax_relief
        pays_rent = add(spm_unit, period, ["rent"]) > 0
        has_elderly_or_disabled = spm_unit("has_usda_elderly_disabled", period)
        elderly_or_disabled_renters = has_elderly_or_disabled & pays_rent

        income = spm_unit("spm_unit_net_income", period)
        size = spm_unit("spm_unit_size", period)
        renter_income_limit = p.ami.ami.calc(size) * p.ami.rate.renter.calc(
            size
        )
        renter_income_eligible = income <= renter_income_limit

        return elderly_or_disabled_renters & renter_income_eligible
