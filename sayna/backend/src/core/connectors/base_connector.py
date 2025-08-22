"""
Base Connector for SAYNA Voice OS.
Defines the interface and common functionality for all system connectors.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class ConnectorState(str, Enum):
    """Possible states of a connector."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class AuthType(str, Enum):
    """Supported authentication types."""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"


@dataclass
class ConnectorConfig:
    """Configuration for a connector."""
    name: str
    auth_type: AuthType
    auth_config: Dict[str, Any]
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True


class ConnectorHealth(BaseModel):
    """Health status of a connector."""
    healthy: bool = Field(..., description="Overall health status")
    status: ConnectorState = Field(..., description="Current state")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional health details")
    last_error: Optional[str] = Field(None, description="Last error message")


class ActionRequest(BaseModel):
    """Request to execute an action."""
    action: str = Field(..., description="Name of the action to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    timeout: Optional[int] = Field(None, description="Custom timeout in seconds")

    @validator('timeout')
    def validate_timeout(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Timeout must be positive")
        return v


class ActionResponse(BaseModel):
    """Response from an action execution."""
    success: bool = Field(..., description="Whether the action succeeded")
    result: Dict[str, Any] = Field(default_factory=dict, description="Action result")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    connector: str = Field(..., description="Connector that executed the action")


class BaseConnector(ABC):
    """Abstract base class for all SAYNA connectors."""

    def __init__(self, config: ConnectorConfig):
        """
        Initialize the connector with configuration.

        Args:
            config: Connector configuration
        """
        self.config = config
        self.state = ConnectorState.DISCONNECTED
        self._connection_lock = asyncio.Lock()
        self._action_lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def initialize(self) -> None:
        """
        Initialize the connector.
        Should be called before any other operations.
        """
        if self.state != ConnectorState.DISCONNECTED:
            self.logger.warning("Connector already initialized")
            return

        self.state = ConnectorState.CONNECTING
        try:
            await self._initialize()
            self.state = ConnectorState.CONNECTED
            self.logger.info("Connector initialized successfully")
        except Exception as e:
            self.state = ConnectorState.ERROR
            self.logger.error(f"Connector initialization failed: {str(e)}")
            raise

    @abstractmethod
    async def _initialize(self) -> None:
        """
        Connector-specific initialization.
        To be implemented by subclasses.
        """
        pass

    async def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action on the connector.

        Args:
            action: Name of the action to execute
            parameters: Parameters for the action

        Returns:
            Dictionary with action result
        """
        if self.state != ConnectorState.CONNECTED:
            raise ConnectionError("Connector is not connected")

        request = ActionRequest(
            action=action,
            parameters=parameters,
            context={"connector": self.config.name}
        )

        async with self._action_lock:
            try:
                start_time = asyncio.get_event_loop().time()
                result = await self._execute(request)
                execution_time = asyncio.get_event_loop().time() - start_time

                return ActionResponse(
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    connector=self.config.name
                ).dict()

            except Exception as e:
                self.logger.error(f"Action '{action}' failed: {str(e)}")
                return ActionResponse(
                    success=False,
                    error=str(e),
                    execution_time=asyncio.get_event_loop().time() - start_time,
                    connector=self.config.name
                ).dict()

    @abstractmethod
    async def _execute(self, request: ActionRequest) -> Dict[str, Any]:
        """
        Connector-specific action execution.
        To be implemented by subclasses.

        Args:
            request: Action request with parameters

        Returns:
            Dictionary with action result
        """
        pass

    async def disconnect(self) -> None:
        """
        Disconnect the connector and clean up resources.
        """
        if self.state == ConnectorState.DISCONNECTED:
            return

        async with self._connection_lock:
            try:
                await self._disconnect()
                self.state = ConnectorState.DISCONNECTED
                self.logger.info("Connector disconnected successfully")
            except Exception as e:
                self.state = ConnectorState.ERROR
                self.logger.error(f"Error disconnecting: {str(e)}")
                raise

    @abstractmethod
    async def _disconnect(self) -> None:
        """
        Connector-specific disconnection.
        To be implemented by subclasses.
        """
        pass

    async def health_check(self) -> ConnectorHealth:
        """
        Check the health of the connector.

        Returns:
            ConnectorHealth: Health status
        """
        try:
            details = await self._health_check()
            healthy = self.state == ConnectorState.CONNECTED

            return ConnectorHealth(
                healthy=healthy,
                status=self.state,
                details=details
            )
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return ConnectorHealth(
                healthy=False,
                status=ConnectorState.ERROR,
                details={"error": str(e)}
            )

    async def _health_check(self) -> Dict[str, Any]:
        """
        Connector-specific health check.
        To be implemented by subclasses.

        Returns:
            Dictionary with health details
        """
        return {"status": "ok"}

    async def get_supported_actions(self) -> List[str]:
        """
        Get list of supported actions.

        Returns:
            List of action names
        """
        return await self._get_supported_actions()

    @abstractmethod
    async def _get_supported_actions(self) -> List[str]:
        """
        Connector-specific action list.
        To be implemented by subclasses.

        Returns:
            List of supported action names
        """
        pass

    async def get_action_schema(self, action: str) -> Dict[str, Any]:
        """
        Get schema for a specific action.

        Args:
            action: Name of the action

        Returns:
            Dictionary describing the action's parameters and requirements
        """
        try:
            return await self._get_action_schema(action)
        except Exception as e:
            self.logger.error(f"Failed to get schema for action '{action}': {str(e)}")
            raise ValueError(f"Action schema unavailable: {str(e)}")

    @abstractmethod
    async def _get_action_schema(self, action: str) -> Dict[str, Any]:
        """
        Connector-specific action schema.
        To be implemented by subclasses.

        Args:
            action: Name of the action

        Returns:
            Dictionary with action schema
        """
        pass

    async def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters for an action.

        Args:
            action: Name of the action
            parameters: Parameters to validate

        Returns:
            Dictionary with validation results
        """
        try:
            schema = await self.get_action_schema(action)
            return await self._validate_parameters(action, parameters, schema)
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }

    async def _validate_parameters(
            self,
            action: str,
            parameters: Dict[str, Any],
            schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate parameters against an action schema.

        Args:
            action: Action name
            parameters: Parameters to validate
            schema: Action schema

        Returns:
            Dictionary with validation results
        """
        # Basic validation that can be overridden by subclasses
        required_params = schema.get("required_parameters", [])
        errors = []
        warnings = []

        # Check for missing required parameters
        missing_params = [p for p in required_params if p not in parameters]
        if missing_params:
            errors.append(f"Missing required parameters: {', '.join(missing_params)}")

        # Check for unexpected parameters
        allowed_params = schema.get("parameters", {}).keys()
        unexpected_params = [p for p in parameters.keys() if p not in allowed_params]
        if unexpected_params:
            warnings.append(f"Unexpected parameters: {', '.join(unexpected_params)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.config.name}, state={self.state})"

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()