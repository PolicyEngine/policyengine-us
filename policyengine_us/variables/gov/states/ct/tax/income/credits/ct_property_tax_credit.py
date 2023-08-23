from policyengine_us.model_api import *


class ct_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "CT property tax credit"
    unit = USD
    definition_period = YEAR
    reference = ()
    defined_for = "ct_ptc_taxunit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        #
