"""
Skill registry – dispatch + Vertex AI Function Calling declarations.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from pydantic import BaseModel


class SkillRegistry:
    def __init__(self):
        self._skills: dict[str, Callable] = {}

    def register(self, fn: Callable) -> None:
        name = getattr(fn, "skill_name", fn.__name__)
        self._skills[name] = fn

    def names(self) -> list[str]:
        return list(self._skills.keys())

    def get(self, name: str) -> Callable:
        if name not in self._skills:
            raise KeyError(f"Unknown skill: {name}")
        return self._skills[name]

    def call(self, name: str, payload: Any) -> BaseModel:
        fn = self.get(name)
        result = fn(payload)
        return result

    def vertex_tool_declarations(
        self, only: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        """
        Emit OpenAPI-style function declarations suitable for Vertex AI
        Function Calling / GenerativeModel tool config.
        """
        decls = []
        for name, fn in self._skills.items():
            if only is not None and name not in only:
                continue
            input_model = getattr(fn, "input_model", None)
            description = getattr(fn, "skill_description", fn.__doc__ or name)
            parameters: dict[str, Any]
            if input_model is not None and issubclass(input_model, BaseModel):
                schema = input_model.model_json_schema()
                # Vertex expects a subset of JSON Schema
                parameters = {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                }
            else:
                parameters = {"type": "object", "properties": {}}
            decls.append(
                {
                    "name": name,
                    "description": description.strip(),
                    "parameters": parameters,
                }
            )
        return decls

    def estimate_tool_tokens(self, only: Optional[list[str]] = None) -> int:
        """Rough token estimate for tool declarations (~4 chars / token)."""
        import json

        decls = self.vertex_tool_declarations(only=only)
        return max(1, len(json.dumps(decls)) // 4)


def build_default_registry() -> SkillRegistry:
    from .skills_syntax import validate_dfd_syntax
    from .skills_graph import check_trust_boundary_paths
    from .skills_policy import match_security_controls
    from .skills_score import score_sdlc_compliance

    reg = SkillRegistry()
    for fn in (
        validate_dfd_syntax,
        check_trust_boundary_paths,
        match_security_controls,
        score_sdlc_compliance,
    ):
        reg.register(fn)
    return reg
