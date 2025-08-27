# Example Template Creation Plan

## Overview
Generate an example template file (`example-template.json`) based on the existing personal configuration file (`mine/michael-family-friends-archive-postal.json`) with randomized data for demonstration purposes.

## Transformation Requirements

### 1. Generate randomized names for all archive groups
- Replace each person/group name with common American first names
- For compound names (e.g., "Mom and Dad"), create new compound names with the same pattern
- Maintain the same number of names per group

### 2. Transform server configuration with randomized values
- Change server host from personal to generic example
- Replace personal email with example email address

### 3. Update name fields and destination folders
- Replace "name" field values with randomized names
- Update corresponding folder paths in "destination_folder" to match new names
- Preserve existing folder structure (Personal/Special People/Family vs Friends)

### 4. Transform text_match email addresses
- Replace existing email addresses with new ones based on randomized names
- Maintain similar email patterns and providers
- Use randomized but realistic email formats

### 5. Transform regex_match patterns with new names and domains
- Keep the same regex structure and pattern complexity as original
- Replace username parts (before @) with variations of new randomized names
- Replace domain names with generic example domains (example.com, testdomain.org, sampledomain.net)
- Preserve alternation patterns and regex syntax

### 6. Write the example-template.json file
- Create the final file in the root directory
- Ensure all transformations are applied consistently
- Maintain valid JSON structure and functionality

## Key Considerations
- Preserve the exact JSON structure and configuration functionality
- Ensure all personal information is completely anonymized
- Maintain realistic but generic example data
- Keep the same email matching patterns and complexity for demonstration purposes