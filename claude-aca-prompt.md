## Specific Files to Modify
- policyengine_us/parameters/gov/aca
- policyengine_us/variables/gov/aca
- policyengine_us/tests/policy/baseline/gov/aca


## Implementation Notes
- Keep the code modular to allow easy addition of other states that use family tiers
- Consider creating a state configuration flag to identify family tier states
- Ensure backward compatibility with states using traditional age curve rating


##Prompt for Claude Code: Implementing ACA Family Tier Ratings
#Background
Your task is to modify the ACA premium calculation system to support states that use family tier ratings (like New York and Vermont) instead of summing individual age-rated premiums.

#Current Process

Find household's rating area from county
Find base cost at age 0 using YAML files
Apply age curves to each household member
Sum individual premiums
Apply subsidies

#Family Tier Rating System
New York and Vermont use standardized family tiers instead of summing individual premiums:
New York's Official Rating Tiers:

Single = 1.00
Single + Spouse = 2.00
Single + Child(ren) = 1.70
Single + Spouse + Child(ren) = 2.85
Child only = 0.412 (no adults at all)

#Vermont's Rating Tiers:

One Adult = 1
Two Adults = 2
One Adult and One or More Children = 1.93
Two Adults and One or More Children = 2.81

#Implementation Requirements

For NY and VT, family tier should be applied after step 2 (base cost) and replace steps 3-4
For NY, age definition:

Members 19 and under = children
Members 20 and up = adults


#For NY's age curve, use:

Ages 0-20: 0.412 multiplier
Ages 21+: 1.0 multiplier
Only use the .412 if there are no adults in the household

Task
Modify the premium calculation pipeline to detect when a state uses family tiers and apply the appropriate tier multiplier instead of summing individual age-rated premiums. Also generate unit tests following the previous formatting of existing test files
