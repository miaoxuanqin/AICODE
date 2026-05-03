# Import all models to ensure relationships are properly registered
from app.models.user import User
from app.models.organization import Organization
from app.models.role import Role, Permission, RolePermission, UserRole
from app.models.access_control import KnowledgeAccess
from app.models.knowledge import Knowledge, UserFavorite, KnowledgeComment
from app.models.qa import QARecord, QAHotQuestion, QAHistory
from app.models.category import Category