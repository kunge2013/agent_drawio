"""Chat and conversation endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

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
    Send a message and get AI-generated response with diagrams.

    This is the main endpoint that orchestrates the entire flow:
    1. Saves user message
    2. Generates prototype design via LLM
    3. Generates UI flow diagram
    4. Generates business flow diagram
    5. Generates design documentation
    6. Saves all generated content
    7. Returns AI response

    Args:
        request: Message request with conversation ID
        db: Database session

    Returns:
        AI response with generated content
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
        history = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()

        history_list = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]

        # Generate prototype design
        prototype_data = await langchain_service.generate_prototype(
            request.message,
            history_list
        )

        # Generate UI flow
        ui_flow_data = await langchain_service.generate_ui_flow(
            prototype_data,
            request.message
        )
        ui_flow_xml = drawio_generator.generate_ui_flow_diagram(
            ui_flow_data["flow_data"]
        )

        # Generate business flow
        business_flow_data = await langchain_service.generate_business_flow(
            request.message,
            prototype_data
        )
        business_flow_xml = drawio_generator.generate_business_flow_diagram(
            business_flow_data["business_flow"]
        )

        # Generate documentation
        all_data = {
            "prototype": prototype_data,
            "ui_flow": ui_flow_data,
            "business_flow": business_flow_data
        }
        documentation = await langchain_service.generate_documentation(all_data)

        # Save design
        from app.models.design import Design
        design = Design(
            conversation_id=conversation.id,
            name=f"Design for conversation {conversation.id}",
            description=request.message,
            prototype_data=prototype_data,
            documentation=documentation
        )
        db.add(design)
        db.commit()
        db.refresh(design)

        # Save diagrams
        from app.models.diagram import Diagram

        ui_diagram = Diagram(
            design_id=design.id,
            diagram_type="ui_flow",
            title="UI Flow Diagram",
            drawio_xml=ui_flow_xml,
            flow_data=ui_flow_data["flow_data"]
        )
        db.add(ui_diagram)

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
        screens_count = len(prototype_data.get("screens", []))
        ui_nodes_count = len(ui_flow_data["flow_data"].get("nodes", []))
        business_processes_count = len(
            business_flow_data["business_flow"].get("processes", [])
        )

        assistant_message = f"""Based on your requirements, I've generated:

**1. Prototype Design**
{prototype_data.get('prototype_description', 'See prototype panel')}

**2. UI Flow Diagram**
{ui_nodes_count} screens identified with navigation flows.

**3. Business Process Flow**
{business_processes_count} process steps defined.

**4. Design Documentation**
Comprehensive documentation explaining the design philosophy and decisions.

You can export the diagrams as .drawio files from the panels on the right."""

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
                "prototype": prototype_data.get("prototype_description"),
                "ui_flow": {
                    "diagram_id": ui_diagram.id,
                    "preview": f"<p>UI Flow with {ui_nodes_count} screens</p>",
                    "xml": ui_flow_xml
                },
                "business_flow": {
                    "diagram_id": business_diagram.id,
                    "preview": f"<p>Business Flow with {business_processes_count} steps</p>",
                    "xml": business_flow_xml
                },
                "documentation": documentation
            }
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
