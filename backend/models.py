from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class IncidentCreate(BaseModel):
    description: str
    system: str
    version: str
    category: str
    severity: str
    impact_level: Optional[str] = "LOW"

class RecommendationResponse(BaseModel):
    recommendation_id: str
    title: str
    description: str
    relevance_score: float  # Percentage 0-100
    score_breakdown: Dict[str, float]
    system_compatibility: bool
    version_compatibility: bool
    is_outdated: bool
    outdated_reason: Optional[str] = None
    historical_count: int
    successful_count: int
    avg_ttr: float
    knowledge_article_id: Optional[str] = None
    knowledge_article_status: str
    last_verified: str
    impact_level: str
    requires_human_confirmation: bool
    steps: Optional[List[str]] = []
    rules_passed: List[str]
    historical_ticket_ids: List[Dict[str, Any]]

class EvidenceDetails(BaseModel):
    recommendation_id: str
    title: str
    relevance_score: float
    score_breakdown: Dict[str, float]
    rules_passed: List[str]
    historical_incidents: List[Dict[str, Any]]
    knowledge_article: Optional[Dict[str, Any]]
    system_version: str
    last_verified: str
    version_compat_details: Dict[str, Any]

class ActionConfirmationRequest(BaseModel):
    action: str  # "APPROVE" or "REJECT"
    recommendation_id: str
    override_reason: Optional[str] = None
    override_comment: Optional[str] = None

class EventInjectRequest(BaseModel):
    event_type_to_inject: str  # "DUPLICATE", "DELAYED", "OUT_OF_ORDER"
    incident_id: Optional[str] = None

class FeedbackCreate(BaseModel):
    recommendation_id: str
    accepted: bool
    successful: bool
    override_reason: Optional[str] = None
    comment: Optional[str] = None
