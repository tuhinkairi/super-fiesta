
from modules.story_intelligence.models.character import (
    Character,
    CharacterEvidence,
    CharacterExtractionResult,
)


class EntityResolver:
    """
    Identifies duplicate character records and combines
    records connected through explicit aliases.
    """

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normalize names for comparison.

        Example:
        ' Inspector   Arjun ' -> 'inspector arjun'
        """

        return " ".join(name.casefold().split())

    @classmethod
    def _get_identifiers(cls, character: Character) -> set[str]:
        """
        Get the primary name and all known aliases.
        """

        identifiers = {cls._normalize_name(character.name)}

        for alias in character.aliases:
            normalized = cls._normalize_name(alias)

            if normalized:
                identifiers.add(normalized)

        return identifiers

    @staticmethod
    def _unique_strings(values: list[str]) -> list[str]:
        """
        Remove duplicate strings while preserving their order.
        """

        result = []
        seen = set()

        for value in values:
            cleaned = value.strip()

            if not cleaned:
                continue

            key = cleaned.casefold()

            if key not in seen:
                seen.add(key)
                result.append(cleaned)

        return result

    @classmethod
    def _merge_group(
        cls,
        characters: list[Character]
    ) -> Character:
        """
        Combine multiple records belonging to one character.
        """

        # Keep the first extracted name as the canonical name.
        canonical_name = characters[0].name

        aliases = []
        roles = []
        descriptions = []
        traits = []
        evidence = []

        seen_evidence = set()

        for character in characters:

            # Preserve alternative names.
            if (
                cls._normalize_name(character.name)
                != cls._normalize_name(canonical_name)
            ):
                aliases.append(character.name)

            aliases.extend(character.aliases)

            # Collect available roles and descriptions.
            if (
                character.role_in_story
                and character.role_in_story.casefold() != "unknown"
            ):
                roles.append(character.role_in_story)

            if character.description:
                descriptions.append(character.description)

            traits.extend(character.personality_traits)

            # Remove duplicate evidence records.
            for item in character.evidence:
                evidence_key = (
                    item.fact.casefold().strip(),
                    item.quote.strip(),
                    item.evidence_type,
                )

                if evidence_key not in seen_evidence:
                    seen_evidence.add(evidence_key)
                    evidence.append(item)

        # Remove the canonical name from the alias list.
        canonical_normalized = cls._normalize_name(canonical_name)

        aliases = [
            alias
            for alias in cls._unique_strings(aliases)
            if cls._normalize_name(alias) != canonical_normalized
        ]

        roles = cls._unique_strings(roles)
        descriptions = cls._unique_strings(descriptions)
        traits = cls._unique_strings(traits)

        return Character(
            name=canonical_name,
            aliases=aliases,
            role_in_story="; ".join(roles) if roles else "unknown",
            description=" ".join(descriptions),
            personality_traits=traits,
            evidence=evidence,
        )

    @classmethod
    def resolve(
        cls,
        extraction_result: CharacterExtractionResult
    ) -> CharacterExtractionResult:
        """
        Find duplicate records and return unified characters.

        Characters are merged when their names or explicitly
        identified aliases overlap.
        """

        groups = []

        for character in extraction_result.characters:

            identifiers = cls._get_identifiers(character)

            # Find groups that share a name or alias.
            matching_indices = [
                index
                for index, group in enumerate(groups)
                if identifiers.intersection(group["identifiers"])
            ]

            if not matching_indices:
                groups.append({
                    "characters": [character],
                    "identifiers": identifiers,
                })

                continue

            # Add the character to the first matching group.
            first_index = matching_indices[0]

            groups[first_index]["characters"].append(character)
            groups[first_index]["identifiers"].update(identifiers)

            # Merge any other groups connected by this character.
            for index in reversed(matching_indices[1:]):

                other_group = groups.pop(index)

                groups[first_index]["characters"].extend(
                    other_group["characters"]
                )

                groups[first_index]["identifiers"].update(
                    other_group["identifiers"]
                )

        # Create one final character record per group.
        resolved_characters = [
            cls._merge_group(group["characters"])
            for group in groups
        ]

        return CharacterExtractionResult(
            characters=resolved_characters
        )
