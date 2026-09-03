from policyengine_us.model_api import *


class is_usda_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = (
        "Meets the benefit-receipt half of the SNAP 'elderly or disabled "
        "member' definition (7 CFR 271.2), which counts any SSI receipt, "
        "whether based on age, blindness, or disability. SSI is paid only "
        "after SSA has determined the person is aged, blind, or disabled "
        "under section 1614, and that determination does not lapse month to "
        "month, so receipt in any month of the year qualifies for the year."
    )
    label = "USDA disabled status"

    def formula(person, period, parameters):
        programs = parameters(period).gov.usda.disabled_programs
        variables = person.simulation.tax_benefit_system.variables

        def received(program):
            variable = variables[program]
            # Monthly booleans are stocks, which Core reads at December when
            # requested for a year. Sum the months instead so receipt in any
            # month qualifies, matching how monthly amounts are annualized.
            if variable.definition_period == MONTH and variable.value_type == bool:
                return person(program, period, options=[ADD]) > 0
            return person(program, period)

        return np.logical_or.reduce([received(program) for program in programs])
