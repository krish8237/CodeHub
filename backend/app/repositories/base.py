from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def create(self, obj_data: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get(self, id: int) -> Optional[ModelType]:
        """Get a record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Get multiple records with optional filtering and pagination"""
        query = self.db.query(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, id: int, obj_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record by ID"""
        db_obj = self.get(id)
        if db_obj:
            for key, value in obj_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Delete a record by ID"""
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering"""
        query = self.db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    def exists(self, id: int) -> bool:
        """Check if a record exists by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
    
    def bulk_create(self, obj_data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records in bulk"""
        db_objs = [self.model(**obj_data) for obj_data in obj_data_list]
        self.db.add_all(db_objs)
        self.db.commit()
        for db_obj in db_objs:
            self.db.refresh(db_obj)
        return db_objs