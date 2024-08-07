from policyengine_us.model_api import *


class denver_property_tax_relief_renter(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Denver Property Tax Relief for renter"
    definition_period = YEAR
    reference = "https://denvergov.org/files/content/public/v/37/government/agencies-departments-offices/agencies-departments-offices-directory/denver-human-services/be-supported/additional-assistance/property-tax-relief/denver-property-tax-relief-program-year-2021-rules.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.co.denver.property_tax_relief
        has_rent = add(spm_unit, period, ["rent"]) > 0
        has_elderly_or_disabled = spm_unit("has_usda_elderly_disabled", period)
        renter_requirements = has_elderly_or_disabled & has_rent

        income = spm_unit("spm_unit_net_income", period)
        size = spm_unit("spm_unit_size", period)
        renter_income_limit = p.ami.ami.calc(size) * p.ami.rate.renter.calc(
            size
        )
        renter_income_eligible = income <= renter_income_limit

        return where(
            renter_requirements & renter_income_eligible,
            p.maximum_amount.renter,
            0,
        )
