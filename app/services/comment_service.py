from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.service_request import ServiceRequest
from app.models.user import User
from app.middleware.error_handler import AppException

class CommentService:
    
    @staticmethod
    def add_comment(db: Session, request_id: int, user_id: int, comment_text: str, is_internal: bool = False):
        request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not request:
            raise AppException("REQUEST_NOT_FOUND", "Request not found", 404)
        
        comment = Comment(
            request_id=request_id,
            user_id=user_id,
            comment=comment_text,
            is_internal=is_internal
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    
    @staticmethod
    def get_comments(db: Session, request_id: int, user: User):
        request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not request:
            raise AppException("REQUEST_NOT_FOUND", "Request not found", 404)
        
        query = db.query(Comment).filter(Comment.request_id == request_id)
        
        if user.role == "EMPLOYEE":
            query = query.filter(Comment.is_internal == False)
        
        return query.order_by(Comment.created_at.asc()).all()
    
    @staticmethod
    def get_comment_by_id(db: Session, comment_id: int, user: User):
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise AppException("COMMENT_NOT_FOUND", "Comment not found", 404)
        
        request = db.query(ServiceRequest).filter(ServiceRequest.id == comment.request_id).first()
        if not request:
            raise AppException("REQUEST_NOT_FOUND", "Request not found", 404)
        
        if comment.is_internal and user.role == "EMPLOYEE":
            raise AppException("ACCESS_DENIED", "You cannot view internal comments", 403)
        
        return comment
    
    @staticmethod
    def update_comment(db: Session, comment_id: int, user_id: int, comment_text: str):
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise AppException("COMMENT_NOT_FOUND", "Comment not found", 404)
        
        if comment.user_id != user_id:
            raise AppException("ACCESS_DENIED", "You can only update your own comments", 403)
        
        comment.comment = comment_text
        db.commit()
        db.refresh(comment)
        return comment
    
    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int, user_role: str):
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise AppException("COMMENT_NOT_FOUND", "Comment not found", 404)
        
        if comment.user_id != user_id and user_role != "ADMIN":
            raise AppException("ACCESS_DENIED", "You can only delete your own comments", 403)
        
        db.delete(comment)
        db.commit()
        return True
    
    @staticmethod
    def get_comment_count(db: Session, request_id: int):
        total = db.query(Comment).filter(Comment.request_id == request_id).count()
        internal = db.query(Comment).filter(
            Comment.request_id == request_id,
            Comment.is_internal == True
        ).count()
        return {"total": total, "internal": internal, "public": total - internal}
