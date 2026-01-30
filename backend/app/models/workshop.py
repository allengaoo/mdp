"""
Workshop Layer Models for MDP Platform V3.1
Tables: app_definition, app_module, app_widget
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON


# ==========================================
# ORM Models - Workshop App Builder
# ==========================================

class AppDefinition(SQLModel, table=True):
    """Workshop application definition.
    
    App types: DASHBOARD, FORM, EXPLORER, WORKFLOW
    Maps to table: app_definition
    """
    __tablename__ = "app_definition"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    project_id: str = Field(foreign_key="sys_project.id", max_length=36)
    name: str = Field(max_length=100)
    app_type: str = Field(max_length=50)  # DASHBOARD, FORM, EXPLORER, WORKFLOW
    global_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_by: Optional[str] = Field(default=None, max_length=36)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class AppModule(SQLModel, table=True):
    """Application module/page.
    
    Maps to table: app_module
    """
    __tablename__ = "app_module"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    app_id: str = Field(foreign_key="app_definition.id", max_length=36)
    name: Optional[str] = Field(default=None, max_length=100)
    layout_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    display_order: int = Field(default=0)


class AppWidget(SQLModel, table=True):
    """Application widget/component.
    
    Widget types: TABLE, CHART, MAP, FORM, TIMELINE, MEDIA_VIEWER, STAT_CARD, SEARCH, GALLERY
    Maps to table: app_widget
    """
    __tablename__ = "app_widget"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, max_length=36)
    module_id: str = Field(foreign_key="app_module.id", max_length=36)
    widget_type: str = Field(max_length=50)  # TABLE, CHART, MAP, FORM, TIMELINE, MEDIA_VIEWER
    data_binding: Dict[str, Any] = Field(sa_column=Column(JSON))
    view_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    position_config: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


# ==========================================
# DTOs - App Definition
# ==========================================

class AppDefinitionCreate(SQLModel):
    """DTO for creating AppDefinition."""
    project_id: str = Field(max_length=36)
    name: str = Field(max_length=100)
    app_type: str = Field(max_length=50)
    global_config: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = Field(default=None, max_length=36)


class AppDefinitionUpdate(SQLModel):
    """DTO for updating AppDefinition."""
    name: Optional[str] = Field(default=None, max_length=100)
    app_type: Optional[str] = Field(default=None, max_length=50)
    global_config: Optional[Dict[str, Any]] = None


class AppDefinitionRead(SQLModel):
    """DTO for reading AppDefinition."""
    id: str
    project_id: str
    name: str
    app_type: str
    global_config: Optional[Dict[str, Any]]
    created_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class AppDefinitionWithModules(AppDefinitionRead):
    """DTO for App with its modules."""
    modules: list = []


# ==========================================
# DTOs - App Module
# ==========================================

class AppModuleCreate(SQLModel):
    """DTO for creating AppModule."""
    app_id: str = Field(max_length=36)
    name: Optional[str] = Field(default=None, max_length=100)
    layout_config: Optional[Dict[str, Any]] = None
    display_order: int = 0


class AppModuleUpdate(SQLModel):
    """DTO for updating AppModule."""
    name: Optional[str] = Field(default=None, max_length=100)
    layout_config: Optional[Dict[str, Any]] = None
    display_order: Optional[int] = None


class AppModuleRead(SQLModel):
    """DTO for reading AppModule."""
    id: str
    app_id: str
    name: Optional[str]
    layout_config: Optional[Dict[str, Any]]
    display_order: int


class AppModuleWithWidgets(AppModuleRead):
    """DTO for Module with its widgets."""
    widgets: list = []


# ==========================================
# DTOs - App Widget
# ==========================================

class AppWidgetCreate(SQLModel):
    """DTO for creating AppWidget."""
    module_id: str = Field(max_length=36)
    widget_type: str = Field(max_length=50)
    data_binding: Dict[str, Any]
    view_config: Optional[Dict[str, Any]] = None
    position_config: Optional[Dict[str, Any]] = None


class AppWidgetUpdate(SQLModel):
    """DTO for updating AppWidget."""
    widget_type: Optional[str] = Field(default=None, max_length=50)
    data_binding: Optional[Dict[str, Any]] = None
    view_config: Optional[Dict[str, Any]] = None
    position_config: Optional[Dict[str, Any]] = None


class AppWidgetRead(SQLModel):
    """DTO for reading AppWidget."""
    id: str
    module_id: str
    widget_type: str
    data_binding: Dict[str, Any]
    view_config: Optional[Dict[str, Any]]
    position_config: Optional[Dict[str, Any]]
