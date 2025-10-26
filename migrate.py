"""
Migration script untuk update struktur database
Drop old users table dan create new structure
"""

from src.app import create_app
from src.config.database import db

def migrate():
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database migration...")
        
        # Drop all tables manually using raw SQL
        print("\n🗑️  Dropping old tables...")
        try:
            # Disable foreign key checks
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 0'))
            
            # Get all tables
            result = db.session.execute(db.text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'openbo_db'"
            ))
            tables = [row[0] for row in result]
            
            # Drop each table
            for table in tables:
                db.session.execute(db.text(f'DROP TABLE IF EXISTS {table}'))
                print(f"   ✓ Dropped table: {table}")
            
            # Re-enable foreign key checks
            db.session.execute(db.text('SET FOREIGN_KEY_CHECKS = 1'))
            db.session.commit()
            print("✅ Old tables dropped")
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")
            db.session.rollback()
            return
        
        # Create new tables with updated structure
        print("\n📦 Creating new tables...")
        try:
            db.create_all()
            print("✅ New tables created")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return
        
        print("\n✨ Migration completed successfully!")
        print("\nNew tables:")
        result = db.session.execute(db.text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'openbo_db'"
        ))
        for row in result:
            print(f"   - {row[0]}")
        
        print("\n⚠️  Please run 'python seed.py' to create initial data")

if __name__ == '__main__':
    migrate()
