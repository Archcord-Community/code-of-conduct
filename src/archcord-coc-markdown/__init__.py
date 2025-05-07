from pathlib import Path
from datetime import datetime as dt
import json
import sys


class ParseException(Exception):
    pass

class Glossary:
    def __init__(self, word: str, meaning: str) -> None:
        self.word = word
        self.meaning = meaning
        pass
    def __str__(self) -> str:
        return f"- **{self.word}:** {self.meaning}"

class Rule:
    def __init__(self, rule: str, description: str, escalations: list[str], glossary: list[Glossary] = []) -> None:
        self.rule: str = rule
        self.description: str = description
        self.escalations: list[str] = escalations
        self.glossary: list[Glossary] = glossary
        self.redirect_name: str = f"{guess_redirect_name(rule)}"
        self.idx: int = 0
        pass

    def __str__(self) -> str:
        lines = [
            f"{self.description}\n",
        ]

        if self.escalations != []:
            escalations = [    
                "**Punishment Escalation**",
                f"{"\n".join(map(lambda s: f"- {s}", self.escalations))}\n",
            ]
            lines += escalations

        if self.glossary != []:
            glossary = f"{"\n".join(map(str, self.glossary))}\n"
            lines += ["**Glossary**", glossary]

        return "\n".join(lines)

class Section:
    def __init__(self, title: str, description: str, rules: list[Rule] = []) -> None:
        self.title: str = title
        self.description: str = description
        self.rules: list[Rule] = rules
        self.redirect_name: str = guess_redirect_name(title)
        self.idx: int = 0
        pass
    def __str__(self) -> str:
        lines = [
            f"## Section {self.idx} - {self.title} <a name=\"{self.redirect_name}\"></a>\n",
            f"{self.description}\n"
        ]

        for ridx, rule in enumerate(self.rules):
            lines.append(f"### {self.idx}.{ridx + 1} - {rule.rule} <a name=\"{rule.redirect_name}\"></a>\n")
            lines.append(str(rule))

        return "\n".join(lines)
    

def guess_redirect_name(name: str) -> str:
    result = "-".join(map(str.lower, name.split()))
    if not name.isalnum():
        result = ''.join(list(filter(str.isalnum, result)))
    return result

def dict_to_rule(rule_dict: dict[str, any]) -> Rule:
    for key in ["rule", "description", "escalations"]:
        if key not in rule_dict:
            raise ParseException(f"Missing `{key}` in rule: {rule_dict}")
    
    glossary = [Glossary(word["word"], word["meaning"]) for word in rule_dict["glossary"]] if "glossary" in rule_dict else []

    return Rule(rule=rule_dict["rule"], description=rule_dict["description"], escalations=rule_dict["escalations"], glossary=glossary)

def dict_to_section(section_dict: dict[str, str]) -> Section:
    for key in ["title", "description", "rules"]:
        if key not in section_dict:
            raise ParseException(f"Missing `{key}` in rule: {section_dict}")
    
    rules = [ dict_to_rule(rule) for rule in section_dict["rules"] ]
    return Section(section_dict["title"], section_dict["description"], rules)

def main():
    sections_path: Path = Path("sections")
    sections: list[Section] = []
    today = dt.now()

    for sidx, section_file in enumerate(sections_path.iterdir()):
        section_dict = json.loads(section_file.read_text(encoding="utf8"))
        section = dict_to_section(section_dict)
        section.idx = sidx + 1
        for ridx, rule in enumerate(section.rules):
            rule.idx = ridx + 1
            rule.redirect_name = f"section{section.idx}-rule{rule.idx}---" + rule.redirect_name
        sections.append(section)

    joined_sections = "\n".join(map(str, sections))

    lines = [
        "# The Archcord Code of Conduct\n",
        f"## Last edited: {today.strftime("%d/%m/%Y, %H:%M:%S")}\n",
        "**This Code of Conduct only applies to the \"Archcord\" community found at https://discord.gg/QA4Q2pKTGY, for more information please see announcement channels.**"        "---\n",
        "Welcome to the official Archcord community Code of Conduct! We are an inclusive Linux community dedicated to neutrality, moderation transparency, and active community engagement. By joining Archcord, you agree to abide by the rules below as well as Discord's [Community Guidelines](https://discord.com/guidelines) and [Terms of Service](https://discord.com/terms).\n",
        "---\n",
        "## Preface\n",
        "By joining the Archcord community, you agree to follow this Code of Conduct as it exists at the time of joining—and as it is updated over time. You also agree to comply with Discord's [Terms of Service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines). Failure to comply may result in your removal from our community.\n",
        "---\n",
        "## Table Of Contents\n"
    ]

    for section in sections:
        lines.append(f"{section.idx}. [{section.title}](#{section.redirect_name})")
        for rule in section.rules:
            lines.append(f"   - [{section.idx}.{rule.idx} {rule.rule}](#{rule.redirect_name})")

    lines.append(f"\n{joined_sections}")

    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())