from policyengine_us.model_api import *


class tax_unit_files_schedule_f(Variable):
    value_type = bool
    entity = TaxUnit
    label = "required to file Schedule F (Profit or Loss From Farming)"
    documentation = (
        "Whether the tax unit is required to file a federal Schedule F "
        "(Profit or Loss From Farming), or successor form, for the tax year. "
        "Defaults to whether any member has farm operations income; may be "
        "set directly as an input."
    )
    definition_period = YEAR
    reference = "https://www.irs.gov/forms-pubs/about-schedule-f-form-1040"

    def formula(tax_unit, period, parameters):
        # A taxpayer with active farming operations income (or loss) files
        # Schedule F. farm_operations_income is defined as Schedule F income;
        # farm rental income (Form 4835 / Schedule E) is excluded.
        farm_operations_income = add(tax_unit, period, ["farm_operations_income"])
        return farm_operations_income != 0
