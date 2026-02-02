"""
MDP Platform V3.1 - API Routes
RESTful API for V3.1 metadata-driven architecture
"""

from fastapi import APIRouter

from app.api.v3.projects import router as projects_router
from app.api.v3.ontology import router as ontology_router
from app.api.v3.connectors import router as connectors_router, sync_router
from app.api.v3.mapping import router as mapping_router
from app.api.v3.health import router as health_router
from app.api.v3.search import router as search_router
from app.api.v3.graph import router as graph_router
from app.api.v3.object_views import router as object_views_router, objects_router
from app.api.v3.chat import router as chat_router
from app.api.v3.execute import router as execute_router

# Main V3 router (prefix set in main.py as /api/v3)
router = APIRouter(tags=["V3.1 API"])

# Include sub-routers
router.include_router(projects_router)
router.include_router(ontology_router)
router.include_router(connectors_router)
router.include_router(sync_router)
router.include_router(mapping_router)
router.include_router(health_router)
router.include_router(search_router)
router.include_router(graph_router)
router.include_router(object_views_router)
router.include_router(objects_router)
router.include_router(chat_router)
router.include_router(execute_router)

__all__ = ["router"]
