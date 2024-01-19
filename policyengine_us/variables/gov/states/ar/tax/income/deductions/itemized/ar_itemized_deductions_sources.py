from policyengine_us.model_api import *


class ar_itemized_deductions_sources(Variable):
    value_type = float
    entity = TaxUnit
    label = "Sources for the Arkansas itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/AR1075_2022.pdf#page=1"
    defined_for = StateCode.AR
    adds = "gov.states.ar.tax.income.deductions.itemized.sources"
