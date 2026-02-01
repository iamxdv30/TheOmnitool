from main import create_app
from model.users import User
from model.tools import Tool, ToolAccess

def debug_access():
    app = create_app()
    with app.app_context():
        print("\n--- ALL TOOLS IN DATABASE ---")
        tools = Tool.query.all()
        for t in tools:
            print(f"ID: {t.id}, Name: '{t.name}', Route: '{t.route}'")

        print("\n--- USER iamxdv ---")
        user = User.query.filter_by(username='iamxdv').first()
        if user:
            print(f"User ID: {user.id}, Role: {user.role}")

            print("\n--- TOOL ACCESS FOR iamxdv ---")
            accesses = ToolAccess.query.filter_by(user_id=user.id).all()
            if accesses:
                for a in accesses:
                    print(f"  - tool_name: '{a.tool_name}'")
            else:
                print("  NO TOOL ACCESS RECORDS FOUND!")

            print("\n--- CHECKING SPECIFIC ACCESS ---")
            tax_access = ToolAccess.query.filter_by(
                user_id=user.id,
                tool_name='Tax Calculator'
            ).first()
            print(f"  Has 'Tax Calculator' access: {tax_access is not None}")
        else:
            print("User 'iamxdv' not found!")

if __name__ == "__main__":
    debug_access()
