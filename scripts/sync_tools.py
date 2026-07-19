"""
Tool Synchronization Script
This script serves as the Single Source of Truth for available tools.
It ensures the database matches the code definition of tools.
"""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import db, Tool, ToolAccess, ToolCategory, User
from main import create_app

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("sync_tools")

# DEFINITION OF AVAILABLE TOOLS
# This is the master list. If it's here, it goes into the DB.
DEFINED_TOOLS = [
    {
        "name": "Tax Calculator",
        "display_name": "Tax Calculator",
        "description": "Calculate US, Canada, and international VAT taxes",
        "route": "/unified_tax_calculator",
        "icon": "calculator",
        "category_slug": "finance",
        "is_default": True,
        "is_active": True
    },
    {
        "name": "Unix Timestamp Converter",
        "display_name": "Unix Timestamp",
        "description": "Convert Unix timestamps",
        "route": "/convert",
        "icon": "clock",
        "category_slug": "dev",
        "is_default": True,
        "is_active": True
    },
    {
        "name": "Character Counter",
        "display_name": "Character Counter",
        "description": "Count characters in text",
        "route": "/char_counter",
        "icon": "file-text",
        "category_slug": "writing",
        "is_default": True,
        "is_active": True
    },
    {
        "name": "Email Templates",  # Renamed from 'Email Templates management' if needed
        "display_name": "Email Templates",
        "description": "Create and manage email templates",
        "route": "/email_templates",
        "icon": "mail",
        "category_slug": "marketing",
        "is_default": True,
        "is_active": True
    }
]

# TOOLS TO REMOVE/MIGRATE
# Mapping of Old Name -> New Name (None if just delete)
DEPRECATED_TOOLS = {
    "Canada Tax Calculator": "Tax Calculator",
    "US Tax Calculator": "Tax Calculator",
    "Unified Tax Calculator": "Tax Calculator",
    "Email Templates management": "Email Templates",
    # Legacy kebab-case names (migrate to title case)
    "tax-calculator": "Tax Calculator",
    "char-counter": "Character Counter",
    "email-templates": "Email Templates",
    "unix-timestamp": "Unix Timestamp Converter",
}

def sync_tools():
    """
    Idempotent function to sync defined tools with the database.
    1. Creates missing tools.
    2. Updates existing tools (description, route, etc.).
    3. Migrates user access from deprecated tools.
    4. Removes deprecated tools.
    """
    logger.info("Starting Tool Synchronization...")
    
    # DEBUG: Check DB Connection
    try:
        current_db = db.engine.url.render_as_string(hide_password=True)
        logger.info(f"Connected to Database: {current_db}")
        tool_count = Tool.query.count()
        logger.info(f"Current Tool Count in DB: {tool_count}")
    except Exception as e:
        logger.error(f"Failed to check DB state: {e}")
        raise

    # 1. Handle Deprecation & Migration FIRST (before creating new tools)
    # This prevents UNIQUE constraint violations when old and new tools share routes
    for old_name, new_name in DEPRECATED_TOOLS.items():
        old_tool = Tool.query.filter_by(name=old_name).first()
        if not old_tool:
            continue
            
        logger.info(f"Processing deprecated tool: {old_name} -> {new_name}")
        
        # If mapping exists, migrate user access
        if new_name:
            # Ensure new tool exists
            target_tool = Tool.query.filter_by(name=new_name).first()
            if target_tool:
                # Find all users with access to old tool
                old_accesses = ToolAccess.query.filter_by(tool_name=old_name).all()
                for access in old_accesses:
                    # Check if they already have access to new tool
                    if not ToolAccess.query.filter_by(user_id=access.user_id, tool_name=new_name).first():
                        logger.info(f"Migrating access for user {access.user_id} to {new_name}")
                        db.session.add(ToolAccess(user_id=access.user_id, tool_name=new_name))
            
        # Remove old access records
        ToolAccess.query.filter_by(tool_name=old_name).delete()
        
        # Remove old tool
        db.session.delete(old_tool)
        logger.info(f"Removed deprecated tool: {old_name}")

    db.session.commit()
    logger.info("Deprecated tools removed successfully.")

    # 2. Sync Defined Tools (after deprecation to avoid route conflicts)
    # Resolve category slugs once; missing categories are logged and skipped
    # (run scripts/seed_phase1_dashboard_data.py to create them).
    category_by_slug = {c.slug: c for c in ToolCategory.query.all()}

    for tool_def in DEFINED_TOOLS:
        logger.info(f"Checking definition for: {tool_def['name']}")

        category_id = None
        slug = tool_def.get("category_slug")
        if slug:
            category = category_by_slug.get(slug)
            if category:
                category_id = category.id
            else:
                logger.warning(f"Category '{slug}' not found for tool '{tool_def['name']}' - skipping category assignment")

        tool = Tool.query.filter_by(name=tool_def["name"]).first()

        if tool:
            # Check if updates are actually needed to avoid unnecessary DB writes
            updates = []
            if tool.description != tool_def["description"]:
                tool.description = tool_def["description"]
                updates.append("description")

            if tool.route != tool_def["route"]:
                tool.route = tool_def["route"]
                updates.append("route")

            if tool.is_default != tool_def["is_default"]:
                tool.is_default = tool_def["is_default"]
                updates.append("is_default")

            # Check is_active safely
            target_active = tool_def.get("is_active", True)
            if hasattr(tool, "is_active") and tool.is_active != target_active:
                tool.is_active = target_active
                updates.append("is_active")

            target_display = tool_def.get("display_name")
            if target_display and tool.display_name != target_display:
                tool.display_name = target_display
                updates.append("display_name")

            target_icon = tool_def.get("icon")
            if target_icon and tool.icon != target_icon:
                tool.icon = target_icon
                updates.append("icon")

            if category_id is not None and tool.category_id != category_id:
                tool.category_id = category_id
                updates.append("category_id")

            if updates:
                logger.info(f"Updating tool '{tool.name}': {', '.join(updates)}")
            else:
                logger.info(f"Tool '{tool.name}' is up to date.")
        else:
            # Create new
            logger.info(f"Creating new tool: {tool_def['name']}")
            new_tool = Tool(
                name=tool_def["name"],
                description=tool_def["description"],
                route=tool_def["route"],
                is_default=tool_def["is_default"],
                is_active=tool_def.get("is_active", True)
            )
            new_tool.display_name = tool_def.get("display_name")
            new_tool.icon = tool_def.get("icon")
            new_tool.category_id = category_id
            db.session.add(new_tool)
            logger.info(f"Staged creation of {tool_def['name']}")

    try:
        db.session.commit()
        logger.info("Tool Synchronization Completed.")
    except Exception as e:
        logger.error(f"Failed to commit tool definitions: {e}")
        db.session.rollback()
        raise

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        sync_tools()
