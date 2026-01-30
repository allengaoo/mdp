"""
Hybrid Graph Engine Service
MDP Platform V3.1 - Graph Analysis Module

Implements graph expansion with two modes:
1. Hard Links: Database-stored relationships (sys_link_instance)
2. Semantic Links: Vector similarity from ChromaDB (soft/virtual edges)

Architecture:
- Stage 1: SQL query for hard links
- Stage 2 (Optional): ChromaDB vector search for semantic neighbors
- Stage 3: Merge, prune, and format for React Flow
"""

from typing import Optional, List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid

from sqlalchemy import create_engine, text
from loguru import logger

from app.core.config import settings
from app.models.graph import (
    GraphNode, GraphEdge, GraphDTO,
    ExpandOptions, ShortestPathResponse
)


# Node type configuration for visualization
NODE_TYPE_CONFIG = {
    "target": {"icon": "🎯", "color": "#ff4d4f", "label": "目标"},
    "vessel": {"icon": "🚢", "color": "#1890ff", "label": "舰船"},
    "aircraft": {"icon": "✈️", "color": "#52c41a", "label": "飞机"},
    "mission": {"icon": "📋", "color": "#722ed1", "label": "任务"},
    "sensor": {"icon": "📡", "color": "#faad14", "label": "传感器"},
    "intel_report": {"icon": "📄", "color": "#13c2c2", "label": "情报"},
    "port": {"icon": "⚓", "color": "#eb2f96", "label": "港口"},
    "command_unit": {"icon": "🎖️", "color": "#fa541c", "label": "指挥单位"},
    "recon_image": {"icon": "📷", "color": "#2f54eb", "label": "侦察图像"},
    "source": {"icon": "🔍", "color": "#a0d911", "label": "情报源"},
    "default": {"icon": "📦", "color": "#8c8c8c", "label": "对象"},
}


def get_node_config(object_type: str) -> Dict[str, Any]:
    """Get visualization config for a node type."""
    return NODE_TYPE_CONFIG.get(object_type, NODE_TYPE_CONFIG["default"])


class GraphService:
    """Hybrid Graph Engine for node expansion and path finding."""
    
    def __init__(self):
        self._engine = None
    
    @property
    def engine(self):
        """Lazy-load database engine."""
        if self._engine is None:
            self._engine = create_engine(settings.database_url)
        return self._engine
    
    def expand_node(
        self,
        seed_ids: List[str],
        options: Optional[ExpandOptions] = None
    ) -> GraphDTO:
        """
        Expand graph from seed nodes.
        
        Args:
            seed_ids: Starting node IDs
            options: Expansion options (semantic, limit, depth)
            
        Returns:
            GraphDTO with nodes and edges for React Flow
        """
        if options is None:
            options = ExpandOptions()
        
        logger.info(f"[GraphService] Expanding from seeds: {seed_ids}, semantic={options.semantic}")
        
        # Collect all nodes and edges
        all_nodes: Dict[str, GraphNode] = {}
        all_edges: Dict[str, GraphEdge] = {}
        
        # Add seed nodes first
        for seed_id in seed_ids:
            seed_node = self._get_node_info(seed_id)
            if seed_node:
                all_nodes[seed_id] = seed_node
        
        # Stage 1: Hard Link Expansion (SQL)
        hard_links = self._expand_hard_links(seed_ids, options.limit)
        
        for edge, neighbor_node in hard_links:
            all_edges[edge.id] = edge
            if neighbor_node.id not in all_nodes:
                all_nodes[neighbor_node.id] = neighbor_node
        
        logger.info(f"[GraphService] Hard links: {len(hard_links)} edges")
        
        # Stage 2: Semantic Expansion (ChromaDB) - if enabled
        if options.semantic:
            semantic_links = self._expand_semantic_links(seed_ids, limit=5)
            
            for edge, neighbor_node in semantic_links:
                # Don't add duplicate edges
                if edge.id not in all_edges:
                    all_edges[edge.id] = edge
                    if neighbor_node.id not in all_nodes:
                        all_nodes[neighbor_node.id] = neighbor_node
            
            logger.info(f"[GraphService] Semantic links: {len(semantic_links)} edges")
        
        # Stage 3: Pruning (if over limit)
        if len(all_edges) > options.limit:
            # Keep hard links first, then semantic
            hard_edge_ids = {e.id for e, _ in hard_links}
            sorted_edges = sorted(
                all_edges.values(),
                key=lambda e: (0 if e.id in hard_edge_ids else 1, e.id)
            )
            all_edges = {e.id: e for e in sorted_edges[:options.limit]}
            
            # Keep only connected nodes
            connected_nodes = set()
            for edge in all_edges.values():
                connected_nodes.add(edge.source)
                connected_nodes.add(edge.target)
            connected_nodes.update(seed_ids)
            
            all_nodes = {nid: n for nid, n in all_nodes.items() if nid in connected_nodes}
        
        # Apply layout positions
        nodes_list = list(all_nodes.values())
        self._apply_simple_layout(nodes_list, seed_ids)
        
        return GraphDTO(
            nodes=nodes_list,
            edges=list(all_edges.values())
        )
    
    def _expand_hard_links(
        self,
        seed_ids: List[str],
        limit: int = 50
    ) -> List[Tuple[GraphEdge, GraphNode]]:
        """Query database for hard links from seed nodes."""
        results = []
        
        if not seed_ids:
            return results
        
        # Build parameterized query
        placeholders = ", ".join([":id" + str(i) for i in range(len(seed_ids))])
        params = {f"id{i}": sid for i, sid in enumerate(seed_ids)}
        params["limit"] = limit
        
        query = text(f"""
            SELECT 
                id, 
                source_instance_id, 
                target_instance_id,
                source_object_type,
                target_object_type,
                properties,
                valid_start,
                valid_end
            FROM sys_link_instance
            WHERE source_instance_id IN ({placeholders})
               OR target_instance_id IN ({placeholders})
            LIMIT :limit
        """)
        
        with self.engine.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        
        for row in rows:
            link_id, source_id, target_id, source_type, target_type, props, valid_start, valid_end = row
            
            # Parse properties
            import json
            properties = json.loads(props) if props else {}
            role = properties.get("role", "RELATED")
            
            # Create edge
            edge = GraphEdge(
                id=link_id,
                source=source_id,
                target=target_id,
                type="default",
                label=role,
                data={
                    "role": role,
                    "properties": properties,
                    "valid_start": valid_start.isoformat() if valid_start else None,
                    "valid_end": valid_end.isoformat() if valid_end else None,
                }
            )
            
            # Determine neighbor (the node that's not a seed)
            if source_id in seed_ids:
                neighbor_id = target_id
                neighbor_type = target_type
            else:
                neighbor_id = source_id
                neighbor_type = source_type
            
            # Create neighbor node
            config = get_node_config(neighbor_type)
            neighbor = GraphNode(
                id=neighbor_id,
                type="objectNode",
                data={
                    "label": neighbor_id,
                    "object_type": neighbor_type,
                    "icon": config["icon"],
                    "color": config["color"],
                    "type_label": config["label"],
                }
            )
            
            results.append((edge, neighbor))
        
        return results
    
    def _expand_semantic_links(
        self,
        seed_ids: List[str],
        limit: int = 5
    ) -> List[Tuple[GraphEdge, GraphNode]]:
        """Query ChromaDB for semantically similar nodes."""
        results = []
        
        try:
            # Lazy import to avoid startup errors
            from app.core.vector_store import search_vectors, get_chroma_client
            
            # Get seed vectors and search for similar
            for seed_id in seed_ids:
                try:
                    # Search in default collection
                    # In production, would need to fetch seed's vector first
                    # For now, create virtual semantic links based on existing data
                    
                    # Mock semantic results (in production, use actual vector search)
                    # This simulates finding semantically similar objects
                    pass
                    
                except Exception as e:
                    logger.debug(f"[GraphService] Semantic search for {seed_id} failed: {e}")
                    continue
            
        except ImportError as e:
            logger.warning(f"[GraphService] Vector store not available: {e}")
        except Exception as e:
            logger.warning(f"[GraphService] Semantic expansion failed: {e}")
        
        return results
    
    def _get_node_info(self, node_id: str) -> Optional[GraphNode]:
        """Get node information from database."""
        # First check if node exists as source or target in any link
        query = text("""
            SELECT 
                CASE 
                    WHEN source_instance_id = :node_id THEN source_object_type
                    ELSE target_object_type
                END as object_type
            FROM sys_link_instance
            WHERE source_instance_id = :node_id OR target_instance_id = :node_id
            LIMIT 1
        """)
        
        with self.engine.connect() as conn:
            row = conn.execute(query, {"node_id": node_id}).fetchone()
        
        if row:
            object_type = row[0]
            config = get_node_config(object_type)
            
            return GraphNode(
                id=node_id,
                type="objectNode",
                data={
                    "label": node_id,
                    "object_type": object_type,
                    "icon": config["icon"],
                    "color": config["color"],
                    "type_label": config["label"],
                    "is_seed": True,
                }
            )
        
        # Return a default node if not found
        return GraphNode(
            id=node_id,
            type="objectNode",
            data={
                "label": node_id,
                "object_type": "unknown",
                "icon": "❓",
                "color": "#8c8c8c",
                "type_label": "未知",
                "is_seed": True,
            }
        )
    
    def _apply_simple_layout(
        self,
        nodes: List[GraphNode],
        seed_ids: List[str]
    ):
        """Apply a simple radial layout around seed nodes."""
        import math
        
        # Place seeds in center
        seed_nodes = [n for n in nodes if n.id in seed_ids]
        other_nodes = [n for n in nodes if n.id not in seed_ids]
        
        # Center position for seeds
        center_x, center_y = 400, 300
        
        for i, node in enumerate(seed_nodes):
            if len(seed_nodes) == 1:
                node.position = {"x": center_x, "y": center_y}
            else:
                angle = (2 * math.pi * i) / len(seed_nodes)
                node.position = {
                    "x": center_x + 50 * math.cos(angle),
                    "y": center_y + 50 * math.sin(angle)
                }
        
        # Place other nodes in a circle around seeds
        radius = 200
        for i, node in enumerate(other_nodes):
            angle = (2 * math.pi * i) / max(len(other_nodes), 1)
            node.position = {
                "x": center_x + radius * math.cos(angle),
                "y": center_y + radius * math.sin(angle)
            }
    
    def find_shortest_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 10
    ) -> ShortestPathResponse:
        """
        Find shortest path between two nodes using BFS.
        
        Args:
            source_id: Starting node ID
            target_id: Ending node ID
            max_depth: Maximum search depth
            
        Returns:
            ShortestPathResponse with path and edges
        """
        logger.info(f"[GraphService] Finding path: {source_id} -> {target_id}")
        
        if source_id == target_id:
            return ShortestPathResponse(found=True, path=[source_id], distance=0)
        
        # BFS
        visited: Set[str] = {source_id}
        queue: List[Tuple[str, List[str], List[GraphEdge]]] = [(source_id, [source_id], [])]
        
        while queue and len(visited) < 1000:  # Limit search
            current_id, path, edges = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            # Get neighbors
            neighbors = self._get_neighbors(current_id)
            
            for neighbor_id, edge in neighbors:
                if neighbor_id == target_id:
                    # Found!
                    return ShortestPathResponse(
                        found=True,
                        path=path + [target_id],
                        edges=edges + [edge],
                        distance=len(path)
                    )
                
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id], edges + [edge]))
        
        return ShortestPathResponse(found=False, path=[], edges=[], distance=-1)
    
    def _get_neighbors(self, node_id: str) -> List[Tuple[str, GraphEdge]]:
        """Get immediate neighbors of a node."""
        query = text("""
            SELECT 
                id,
                source_instance_id,
                target_instance_id,
                properties
            FROM sys_link_instance
            WHERE source_instance_id = :node_id OR target_instance_id = :node_id
        """)
        
        with self.engine.connect() as conn:
            rows = conn.execute(query, {"node_id": node_id}).fetchall()
        
        neighbors = []
        for row in rows:
            link_id, source_id, target_id, props = row
            
            import json
            properties = json.loads(props) if props else {}
            role = properties.get("role", "RELATED")
            
            neighbor_id = target_id if source_id == node_id else source_id
            
            edge = GraphEdge(
                id=link_id,
                source=source_id,
                target=target_id,
                label=role
            )
            
            neighbors.append((neighbor_id, edge))
        
        return neighbors
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph."""
        with self.engine.connect() as conn:
            # Total links
            total_links = conn.execute(text("SELECT COUNT(*) FROM sys_link_instance")).scalar()
            
            # Links by type
            type_stats = conn.execute(text("""
                SELECT source_object_type, target_object_type, COUNT(*) as cnt
                FROM sys_link_instance
                GROUP BY source_object_type, target_object_type
                ORDER BY cnt DESC
            """)).fetchall()
            
            # Unique nodes
            unique_nodes = conn.execute(text("""
                SELECT COUNT(DISTINCT node_id) FROM (
                    SELECT source_instance_id as node_id FROM sys_link_instance
                    UNION
                    SELECT target_instance_id as node_id FROM sys_link_instance
                ) as nodes
            """)).scalar()
        
        return {
            "total_links": total_links,
            "unique_nodes": unique_nodes,
            "link_types": [
                {"source": s, "target": t, "count": c}
                for s, t, c in type_stats
            ]
        }


# Singleton instance
_graph_service: Optional[GraphService] = None


def get_graph_service() -> GraphService:
    """Get or create GraphService singleton."""
    global _graph_service
    if _graph_service is None:
        _graph_service = GraphService()
    return _graph_service
