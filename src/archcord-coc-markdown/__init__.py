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
        return f"- {self.word}: {self.meaning}"

class Rule:
    def __init__(self, rule: str, description: str, escalations: list[str], glossary: list[Glossary] = []) -> None:
        self.rule: str = rule
        self.description: str = description
        self.escalations: list[str] = escalations
        self.glossary: list[Glossary] = glossary
        pass

    def __str__(self) -> str:
        lines = [
            f"{self.description}\n",
        ]

        if self.escalations != []:
            escalations = [    
                "**Punishment Escalation**",
                "\n".join(map(lambda s: f"- {s}", self.escalations))
            ]
            lines += escalations

        if self.glossary != []:
            glossary = "\n".join(map(str, self.glossary))
            lines += ["\n**Glossary**", f"{glossary}"]

        return "\n".join(lines + ["\n"])

class Section:
    def __init__(self, title: str, description: str, rules: list[Rule] = []) -> None:
        self.title: str = title
        self.description: str = description
        self.rules: list[Rule] = rules
        self.idx: int = 0
        pass
    def __str__(self) -> str:
        redirect_name = "-".join(map(lambda s: s.lower(), self.title.split(" ")))
        lines = [
            f"## Section {self.idx} - {self.title} <a name=\"{redirect_name}\"></a>\n",
            f"{self.description}\n"
        ]

        for ridx, rule in enumerate(self.rules):
            lines.append(f"### {self.idx}.{ridx + 1} - {rule.rule}\n")
            lines.append(str(rule))

        return "\n".join(lines)

def dict_to_rule(rule_dict: dict[str, any]) -> Rule:
    for key in ["rule", "description", "escalations"]:
        if key not in rule_dict:
            raise ParseException(f"A `{key}` must be present for a rule to be valid.")
    
    glossary = [Glossary(word["word"], word["meaning"]) for word in rule_dict["glossary"]] if "glossary" in rule_dict else []

    return Rule(rule=rule_dict["rule"], description=rule_dict["description"], escalations=rule_dict["escalations"], glossary=glossary)

def dict_to_section(section_dict: dict[str, str]) -> Section:
    for key in ["title", "description", "rules"]:
        if key not in section_dict:
            raise ParseException(f"A `{key}` must be present for a section to be valid.")
    
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
        sections.append(section)

    joined_sections = "\n".join(map(str, sections))

    lines = [
        "# The Archcord Code of Conduct\n",
        f"**Last edited: {today.strftime("%d/%m/%Y, %H:%M:%S")}**\n",
        "---\n"
        "Welcome to the official Archcord community Code of Conduct! We are an inclusive Linux community dedicated to neutrality, moderation transparency, and active community engagement. By joining Archcord, you agree to abide by the rules below as well as Discord's [Community Guidelines](https://discord.com/guidelines) and [Terms of Service](https://discord.com/terms).\n",
        "---\n"
        "## Preface\n",
        "By joining the Archcord community, you agree to follow this Code of Conduct as it exists at the time of joining—and as it is updated over time. You also agree to comply with Discord's [Terms of Service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines). Failure to comply may result in your removal from our community.\n",
        "---\n",
        "## Table Of Contents\n"
    ]

    for sidx, section in enumerate(sections):
        redirect_name = "-".join(map(lambda s: s.lower(), section.title.split(" ")))
        lines.append(f"{sidx + 1}. [{section.title}](#{redirect_name})")

    lines.append(f"\n{joined_sections}")

    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())