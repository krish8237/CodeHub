from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    async def create(self, obj_in: Union[Dict[str, Any], ModelType]) -> ModelType:
        """Create a new record"""
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = obj_in
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    async def get_multi(
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
    
    async def update(self, obj_in: ModelType) -> ModelType:
        """Update a record"""
        self.db.commit()
        self.db.refresh(obj_in)
        return obj_in
    
    async def delete(self, id: int) -> bool:
        """Delete a record by ID"""
        db_obj = await self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
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
    
    async def exists(self, id: int) -> bool:
        """Check if a record exists by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
    
    async def bulk_create(self, obj_data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records in bulk"""
        db_objs = [self.model(**obj_data) for obj_data in obj_data_list]
        self.db.add_all(db_objs)
        self.db.commit()
        for db_obj in db_objs:
            self.db.refresh(db_obj)
        return db_objs