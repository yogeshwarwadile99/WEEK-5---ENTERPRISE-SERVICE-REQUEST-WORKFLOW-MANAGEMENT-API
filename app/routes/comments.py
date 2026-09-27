from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.comment import CommentCreate
from app.models.comment import Comment
from app.models.service_request import ServiceRequest
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/requests/{request_id}/comments", tags=["Comments"])

@router.post("/")
async def add_comment(
    request_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if request exists
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Create comment
    comment = Comment(
        request_id=request_id,
        user_id=current_user.id,
        comment=comment_data.comment
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {"success": True, "message": "Comment added successfully", "data": comment}

@router.get("/")
async def get_comments(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if request exists
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Get comments
    comments = db.query(Comment).filter(Comment.request_id == request_id).all()
    return {"success": True, "data": comments}
