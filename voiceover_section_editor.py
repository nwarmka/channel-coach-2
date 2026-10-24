"""Pure script section editing for the voiceover studio.

No generation, billing, database writes, or storage operations occur here.
Sections are strings; their list order is the intended export order.
"""
from voiceover_script_drafts import validate_script_sections, MAX_SECTIONS


def move_script_section(sections, source_index, destination_index):
    validated = validate_script_sections(sections)
    if type(source_index) is not int or type(destination_index) is not int:
        raise ValueError("Section positions must be integers.")
    if not 0 <= source_index < len(validated):
        raise ValueError("Source section is out of range.")
    if not 0 <= destination_index < len(validated):
        raise ValueError("Destination section is out of range.")
    result = list(validated)
    section = result.pop(source_index)
    result.insert(destination_index, section)
    return result


def replace_script_section(sections, index, new_text):
    validated = validate_script_sections(sections)
    if type(index) is not int or not 0 <= index < len(validated):
        raise ValueError("Section position is out of range.")
    result = list(validated)
    result[index] = new_text
    return validate_script_sections(result)


def append_script_section(sections, new_text):
    validated = validate_script_sections(sections)
    if len(validated) >= MAX_SECTIONS:
        raise ValueError("This script already has the maximum number of sections.")
    return validate_script_sections([*validated, new_text])


def remove_script_section(sections, index):
    validated = validate_script_sections(sections)
    if len(validated) == 1:
        raise ValueError("A script must have at least one section.")
    if type(index) is not int or not 0 <= index < len(validated):
        raise ValueError("Section position is out of range.")
    result = list(validated)
    result.pop(index)
    return result
