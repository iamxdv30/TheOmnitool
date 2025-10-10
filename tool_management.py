from flask import current_app
from model import db
from model import Tool, ToolAccess, User


def initialize_tools():
    tools = [
        {
            "name": "Tax Calculator",
            "description": "Calculate taxes",
            "is_default": True,
        },
        {
            "name": "Canada Tax Calculator",
            "description": "Calculate Canadian taxes",
            "is_default": True,
        },
        {
            "name": "Unix Timestamp Converter",
            "description": "Convert Unix timestamps",
            "is_default": False,
        },
        {
            "name": "Character Counter",
            "description": "Count characters in text",
            "is_default": True,
        },
        {
            "name": "Email Templates",
            "description": "Create email templates",
            "is_default": True,
        },
    ]

    for tool_data in tools:
        tool = Tool.query.filter_by(name=tool_data["name"]).first()
        if tool:
            # Update existing tool
            tool.description = tool_data["description"]
            tool.is_default = tool_data["is_default"]
        else:
            # Create new tool
            new_tool = Tool(**tool_data)
            db.session.add(new_tool)

    db.session.commit()
    print("Tools initialized/updated successfully")


def add_new_tool(name, description, is_default=False):
    tool = Tool.query.filter_by(name=name).first()
    if tool:
        print(f"Tool '{name}' already exists.")
        return

    new_tool = Tool(name=name, description=description, is_default=is_default)
    db.session.add(new_tool)
    db.session.commit()
    print(f"New tool '{name}' added successfully.")

def assign_default_tools_to_user(user_id):
    user = User.query.get(user_id)
    if not user:
        print(f"User with ID {user_id} not found.")
        return

    default_tools = Tool.query.filter_by(is_default=True).all()
    for tool in default_tools:
        if not ToolAccess.query.filter_by(user_id=user.id, tool_name=tool.name).first():
            new_access = ToolAccess(user_id=user.id, tool_name=tool.name)
            db.session.add(new_access)

    db.session.commit()
    print(f"Default tools assigned to user {user.username}")


def list_all_tools():
    tools = Tool.query.all()
    for tool in tools:
        print(
            f"Name: {tool.name}, Description: {tool.description}, Default: {tool.is_default}"
        )


def assign_email_templates_to_users():
    email_templates_tool = Tool.query.filter_by(name="Email Templates").first()
    if email_templates_tool:
        users = User.query.all()
        for user in users:
            if not ToolAccess.query.filter_by(
                user_id=user.id, tool_name="Email Templates"
            ).first():
                new_access = ToolAccess(user_id=user.id, tool_name="Email Templates")
                db.session.add(new_access)
        db.session.commit()
        print("Email Templates tool assigned to all users")
    else:
        print("Email Templates tool not found in the database")




if __name__ == "__main__":
    # This allows you to run this file directly to manage tools
    from main import create_app

    app = create_app()
    with app.app_context():
        while True:
            print("\n1. Initialize/Update Tools")
            print("2. Add New Tool")
            print("3. List All Tools")
            print("4. Assign Default Tools to User")
            print("5. Assign Email Templates to All Users")
            print("6. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                initialize_tools()
            elif choice == "2":
                name = input("Enter tool name: ")
                description = input("Enter tool description: ")
                is_default = input("Is this a default tool? (y/n): ").lower() == "y"
                add_new_tool(name, description, is_default)
            elif choice == "3":
                list_all_tools()
            elif choice == "4":
                user_id = int(input("Enter user ID: "))
                assign_default_tools_to_user(user_id)
            elif choice == "5":
                assign_email_templates_to_users()
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")
