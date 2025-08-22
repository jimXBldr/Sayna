"""
Capability Registry for SAYNA Voice OS.
Manages available system capabilities and their metadata.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field, validator
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class CapabilityCategory(str, Enum):
    """Categories for system capabilities."""
    PRODUCTIVITY = "productivity"
    COMMUNICATION = "communication"
    FINANCE = "finance"
    SYSTEM = "system"
    UTILITY = "utility"


class ParameterType(str, Enum):
    """Supported parameter types for capability actions."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    EMAIL = "email"
    PHONE = "phone"
    PERSON = "person"
    MONEY = "money"
    FILE = "file"
    AUDIO = "audio"
    TEXT = "text"


@dataclass
class ParameterDefinition:
    """Definition of a parameter for capability actions."""
    name: str
    type: ParameterType
    description: str = ""
    required: bool = True
    default: Optional[Union[str, int, float, bool]] = None
    constraints: Optional[Dict[str, Any]] = None
    example: Optional[str] = None


class ActionDefinition(BaseModel):
    """Definition of an action within a capability."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    parameters: List[ParameterDefinition] = Field(default_factory=list)
    returns: Dict[str, str] = Field(default_factory=dict)
    examples: List[str] = Field(default_factory=list)
    requires_confirmation: bool = Field(default=False)
    confirmation_prompt: Optional[str] = Field(None, min_length=10, max_length=200)

    @validator('examples')
    def validate_examples(cls, v):
        if len(v) > 5:
            raise ValueError("Maximum of 5 examples allowed")
        return v


class CapabilityDefinition(BaseModel):
    """Definition of a system capability."""
    id: str = Field(..., regex=r'^[a-z0-9_]+$', min_length=3, max_length=50)
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: CapabilityCategory
    connector: str = Field(..., min_length=3, max_length=50)
    actions: Dict[str, ActionDefinition] = Field(default_factory=dict)
    languages: List[str] = Field(default_factory=list)
    version: str = Field("1.0.0", regex=r'^\d+\.\d+\.\d+$')
    enabled: bool = Field(default=True)
    requires_authentication: bool = Field(default=False)
    offline_support: bool = Field(default=False)

    @validator('languages')
    def validate_languages(cls, v):
        if not v:
            raise ValueError("At least one language must be specified")
        return v


class CapabilityRegistry:
    """Registry of available system capabilities."""

    def __init__(self):
        self.capabilities: Dict[str, CapabilityDefinition] = {}
        self.loaded = False
        self.capabilities_dir = Path("data/capabilities")
        self._capability_index: Dict[str, Set[str]] = {}  # For fast lookup

    async def load_capabilities(self, force_reload: bool = False) -> None:
        """Load capabilities from definition files."""
        if self.loaded and not force_reload:
            return

        if not self.capabilities_dir.exists():
            self.capabilities_dir.mkdir(parents=True, exist_ok=True)
            logger.warning(f"Created capabilities directory at {self.capabilities_dir}")

        self.capabilities = {}
        self._capability_index = {
            "by_category": defaultdict(set),
            "by_language": defaultdict(set),
            "by_action": defaultdict(set)
        }

        loaded_files = 0
        for capability_file in self.capabilities_dir.glob("*.json"):
            try:
                capability = await self._load_capability_file(capability_file)
                if capability.id in self.capabilities:
                    logger.warning(f"Duplicate capability ID: {capability.id} in {capability_file}")
                    continue

                self.capabilities[capability.id] = capability
                self._update_index(capability)
                loaded_files += 1

            except Exception as e:
                logger.error(f"Error loading capability from {capability_file}: {str(e)}")
                continue

        self.loaded = True
        logger.info(f"Loaded {loaded_files} capability definitions with {len(self.capabilities)} valid capabilities")

    async def _load_capability_file(self, file_path: Path) -> CapabilityDefinition:
        """Load and validate a single capability file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate basic structure
        if not isinstance(data, dict):
            raise ValueError("Capability file must contain a JSON object")

        # Convert actions to proper format if they're in a list
        if 'actions' in data and isinstance(data['actions'], list):
            data['actions'] = {action['name']: action for action in data['actions']}

        return CapabilityDefinition(**data)

    def _update_index(self, capability: CapabilityDefinition) -> None:
        """Update the capability index for fast lookups."""
        # Index by category
        self._capability_index['by_category'][capability.category].add(capability.id)

        # Index by language
        for lang in capability.languages:
            self._capability_index['by_language'][lang].add(capability.id)

        # Index by action
        for action_name in capability.actions:
            self._capability_index['by_action'][action_name].add(capability.id)

    async def get_capability(self, capability_id: str) -> Optional[CapabilityDefinition]:
        """Get a capability by ID."""
        if not self.loaded:
            await self.load_capabilities()

        return self.capabilities.get(capability_id)

    async def list_capabilities(
            self,
            enabled_only: bool = True,
            include_actions: bool = False
    ) -> List[Union[CapabilityDefinition, Dict[str, Any]]]:
        """List all available capabilities."""
        if not self.loaded:
            await self.load_capabilities()

        capabilities = list(self.capabilities.values())

        if enabled_only:
            capabilities = [c for c in capabilities if c.enabled]

        if not include_actions:
            return capabilities

        # Include action summaries if requested
        return [{
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "category": c.category,
            "connector": c.connector,
            "actions": list(c.actions.keys()),
            "languages": c.languages,
            "version": c.version
        } for c in capabilities]

    async def find_capabilities(
            self,
            intent: Optional[str] = None,
            category: Optional[Union[CapabilityCategory, str]] = None,
            language: Optional[str] = None,
            enabled_only: bool = True
    ) -> List[CapabilityDefinition]:
        """Find capabilities matching criteria."""
        if not self.loaded:
            await self.load_capabilities()

        # Start with all capabilities
        candidate_ids = set(self.capabilities.keys())

        # Filter by category if specified
        if category:
            if isinstance(category, str):
                try:
                    category = CapabilityCategory(category.lower())
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid category: {category}. Valid categories are: {list(CapabilityCategory)}"
                    )

            category_ids = self._capability_index['by_category'].get(category, set())
            candidate_ids &= category_ids

        # Filter by language if specified
        if language:
            language_ids = self._capability_index['by_language'].get(language, set())
            candidate_ids &= language_ids

        # Filter by intent/action if specified
        if intent:
            action_ids = self._capability_index['by_action'].get(intent, set())
            candidate_ids &= action_ids

        # Get the matching capabilities
        results = [self.capabilities[cid] for cid in candidate_ids]

        # Filter by enabled status if requested
        if enabled_only:
            results = [c for c in results if c.enabled]

        # Sort by capability name
        return sorted(results, key=lambda c: c.name)

    async def get_action(
            self,
            capability_id: str,
            action_name: str
    ) -> Optional[ActionDefinition]:
        """Get an action definition from a capability."""
        capability = await self.get_capability(capability_id)
        if not capability:
            return None

        return capability.actions.get(action_name)

    async def validate_action_parameters(
            self,
            capability_id: str,
            action_name: str,
            parameters: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Validate parameters against an action's requirements."""
        action = await self.get_action(capability_id, action_name)
        if not action:
            return {"errors": [f"Action {action_name} not found in capability {capability_id}"]}

        errors = []
        warnings = []
        provided_params = set(parameters.keys())
        required_params = {p.name for p in action.parameters if p.required}

        # Check for missing required parameters
        missing_params = required_params - provided_params
        if missing_params:
            errors.append(f"Missing required parameters: {', '.join(missing_params)}")

        # Check parameter types
        param_defs = {p.name: p for p in action.parameters}
        for param_name, param_value in parameters.items():
            if param_name not in param_defs:
                warnings.append(f"Unexpected parameter: {param_name}")
                continue

            param_def = param_defs[param_name]
            try:
                self._validate_parameter_value(param_def, param_value)
            except ValueError as e:
                errors.append(str(e))

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _validate_parameter_value(self, param_def: ParameterDefinition, value: Any) -> None:
        """Validate a single parameter value against its definition."""
        # Check type
        if param_def.type == ParameterType.STRING and not isinstance(value, str):
            raise ValueError(f"Parameter {param_def.name} must be a string")

        elif param_def.type == ParameterType.NUMBER:
            if not isinstance(value, (int, float)):
                raise ValueError(f"Parameter {param_def.name} must be a number")

        elif param_def.type == ParameterType.BOOLEAN and not isinstance(value, bool):
            raise ValueError(f"Parameter {param_def.name} must be a boolean")

        # Check constraints
        if param_def.constraints:
            if param_def.type == ParameterType.STRING:
                min_len = param_def.constraints.get("min_length")
                max_len = param_def.constraints.get("max_length")
                if min_len is not None and len(value) < min_len:
                    raise ValueError(
                        f"Parameter {param_def.name} must be at least {min_len} characters"
                    )
                if max_len is not None and len(value) > max_len:
                    raise ValueError(
                        f"Parameter {param_def.name} must be at most {max_len} characters"
                    )

            elif param_def.type == ParameterType.NUMBER:
                minimum = param_def.constraints.get("min")
                maximum = param_def.constraints.get("max")
                if minimum is not None and value < minimum:
                    raise ValueError(
                        f"Parameter {param_def.name} must be at least {minimum}"
                    )
                if maximum is not None and value > maximum:
                    raise ValueError(
                        f"Parameter {param_def.name} must be at most {maximum}"
                    )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on capability registry."""
        if not self.loaded:
            await self.load_capabilities()

        return {
            "healthy": True,
            "loaded": self.loaded,
            "capability_count": len(self.capabilities),
            "enabled_capabilities": len([c for c in self.capabilities.values() if c.enabled]),
            "categories": list({c.category for c in self.capabilities.values()}),
            "languages": list({
                lang
                for c in self.capabilities.values()
                for lang in c.languages
            }),
            "actions": len(self._capability_index['by_action'])
        }