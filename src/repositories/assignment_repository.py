from typing import List, Optional
from src.models.assignment import Assignment
from src.config.database import db

class AssignmentRepository:
    """Repository for Assignment operations"""
    
    def get_all(self) -> List[Assignment]:
        """Get all assignments"""
        return Assignment.query.order_by(Assignment.due_date.asc()).all()
    
    def get_by_id(self, assignment_id: int) -> Optional[Assignment]:
        """Get assignment by ID"""
        return Assignment.query.get(assignment_id)
    
    def get_by_department(self, department_id: int) -> List[Assignment]:
        """Get all assignments for specific department"""
        return Assignment.query.filter_by(department_id=department_id).all()
    
    def create(self, assignment_data: dict) -> Assignment:
        """Create new assignment"""
        assignment = Assignment(
            title=assignment_data.get('title'),
            description=assignment_data.get('description'),
            created_by=assignment_data.get('created_by'),
            department_id=assignment_data.get('department_id'),
            due_date=assignment_data.get('due_date')
        )
        db.session.add(assignment)
        db.session.commit()
        db.session.refresh(assignment)
        return assignment
    
    def update(self, assignment_id: int, update_data: dict) -> Optional[Assignment]:
        """Update assignment"""
        assignment = self.get_by_id(assignment_id)
        if assignment:
            if 'title' in update_data:
                assignment.title = update_data['title']
            if 'description' in update_data:
                assignment.description = update_data['description']
            if 'due_date' in update_data:
                assignment.due_date = update_data['due_date']
            if 'department_id' in update_data:
                assignment.department_id = update_data['department_id']
            db.session.commit()
            db.session.refresh(assignment)
        return assignment
    
    def delete(self, assignment_id: int) -> bool:
        """Delete assignment"""
        assignment = self.get_by_id(assignment_id)
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
            return True
        return False
