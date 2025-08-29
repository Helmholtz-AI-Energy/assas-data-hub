"""Test the admin page database connection."""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from flask_app.database.user_manager import UserManager


def test_admin_connection():
    """Test the connection that the admin page will use."""
    try:
        print("Testing admin page database connection...")

        # This uses the same UserManager that the admin page uses
        user_manager = UserManager()

        # Get users like the admin page does
        all_users = user_manager.get_all_users()

        print(f"✅ Connection successful!")
        print(f"📊 Found {len(all_users)} users")

        if all_users:
            print("👥 Sample users:")
            for user in all_users[:5]:  # Show first 5 users
                username = user.get("username", "unknown")
                email = user.get("email", "no email")
                roles = user.get("roles", [])
                provider = user.get("provider", "unknown")
                print(f"  - {username} ({email}) - {roles} - {provider}")
        else:
            print("❌ No users found!")

        return len(all_users) > 0

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_admin_connection()
    if success:
        print("\n✅ The admin page should now show users!")
    else:
        print("\n❌ Admin page will still show no users. Check the connection.")
