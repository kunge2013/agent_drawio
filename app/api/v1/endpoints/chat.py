"""Chat and conversation endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.schemas.message import (
    MessageRequest,
    MessageResponse,
    ConversationCreate,
    ConversationResponse
)
from app.services import LangChainService, DrawIOGenerator, DesignService
from app.models.base import get_db
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter()


@router.post("/conversation", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.

    Args:
        conversation_data: Conversation creation data
        db: Database session

    Returns:
        Created conversation data
    """
    conversation = Conversation(
        title=conversation_data.title or "New Conversation",
        status="active"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        status=conversation.status
    )


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get conversation details by ID.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Conversation data
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        status=conversation.status
    )


@router.post("/message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a message and get AI-generated business process flow diagram.

    This endpoint:
    1. Saves user message
    2. Generates business process flow diagram via LLM
    3. Saves all generated content
    4. Returns AI response with diagram

    Args:
        request: Message request with conversation ID
        db: Database session

    Returns:
        AI response with generated business flow diagram
    """
    # Initialize services
    langchain_service = LangChainService()
    drawio_generator = DrawIOGenerator()
    design_service = DesignService(db)

    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
            status="active"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()

    try:
        # Get conversation history
        history: List[Message] = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()

        history_list = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]

        # Generate business flow
        business_flow_data = await langchain_service.generate_business_flow(
            request.message,
            history_list
        )
        business_flow_xml = drawio_generator.generate_business_flow_diagram(
            business_flow_data["business_flow"]
        )

        # Save design
        from app.models.design import Design
        design = Design(
            conversation_id=conversation.id,
            name=f"Business Flow for conversation {conversation.id}",
            description=request.message
        )
        db.add(design)
        db.commit()
        db.refresh(design)

        # Save diagram
        from app.models.diagram import Diagram
        business_diagram = Diagram(
            design_id=design.id,
            diagram_type="business_flow",
            title="Business Process Flow",
            drawio_xml=business_flow_xml,
            flow_data=business_flow_data["business_flow"]
        )
        db.add(business_diagram)
        db.commit()

        # Generate assistant response
        business_processes_count = len(
            business_flow_data["business_flow"].get("processes", [])
        )
        decisions_count = len(
            business_flow_data["business_flow"].get("decisions", [])
        )

        assistant_message = f"""Based on your requirements, I've generated a **Business Process Flow** diagram with:

- **{business_processes_count}** process steps
- **{decisions_count}** decision points

The diagram shows the complete flow of your business process, including all actors, processes, and decision branches.

You can view the diagram in the panel and export it as a .drawio file."""

        # Save assistant message
        bot_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message
        )
        db.add(bot_message)
        db.commit()

        return MessageResponse(
            message_id=bot_message.id,
            conversation_id=conversation.id,
            message=assistant_message,
            generated_content={
                "business_flow": {
                    "diagram_id": business_diagram.id,
                    "preview": business_flow_data["raw_response"],
                    "xml": business_flow_xml
                }
            }
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
