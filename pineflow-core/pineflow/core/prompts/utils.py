import re


class SafeFormatter(dict):
    """A dictionary that returns the placeholder as a string if a key is missing."""

    def __missing__(self, key):
        return "{" + key + "}"


def extract_template_vars(template_str: str, input_text: str):
    """
    Extracts variables values from template string into a dictionary.
    Support fuzzy changes between `template_str` and `input_text`.
    """
    parts = re.split(r"({.*?})", template_str)

    regex_pattern = ""
    template_vars = []

    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            template_var = part[1:-1].strip()
            template_vars.append(template_var)
            regex_pattern += r"(.*?)"  # non-greedy capture group
        else:
            # Escape and normalize whitespace
            escaped = re.escape(part)
            # Replace escaped whitespace characters (tabs, newlines) with \s+
            escaped = re.sub(r"\\[ \t\r\n]+", r"\\s*", escaped)
            regex_pattern += escaped

    # Add trailing optional whitespace
    regex_pattern += r"\s*"

    # Compile regex with DOTALL to match newlines in captured groups
    pattern = re.compile(regex_pattern, re.DOTALL)
    match = pattern.fullmatch(input_text)

    if not match:
        return {}

    groups = match.groups()
    return dict(zip(template_vars, [g.strip() for g in groups]))
