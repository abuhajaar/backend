"""
Seed script untuk membuat initial data lengkap
"""

from datetime import datetime
import random
from src.app import create_app
from src.config.database import db
from src.models.user import User
from src.models.department import Department
from src.models.floor import Floor
from src.models.space import Space
from src.models.amenity import Amenity
from src.models.blackout import Blackout
from src.models.booking import Booking

def seed_data():
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Create Departments
        print("\n📁 Creating departments...")
        departments_data = [
            {'id': 1, 'name': 'Engineering', 'manager_id': None},
            {'id': 2, 'name': 'People Ops', 'manager_id': None}
        ]
        
        for dept_data in departments_data:
            dept = Department.query.filter_by(id=dept_data['id']).first()
            if not dept:
                dept = Department(
                    id=dept_data['id'],
                    name=dept_data['name'],
                    manager_id=dept_data['manager_id']
                )
                db.session.add(dept)
                print(f"✅ Created department: {dept.name}")
            else:
                print(f"⚠️  Department already exists: {dept.name}")
        
        db.session.commit()
        
        # Create Users
        print("\n👤 Creating users...")
        users_data = [
            {
                'id': 1, 'username': 'superadmin', 'phone': '+62-811-0000-001',
                'email': 'superadmin@company.com', 'password': 'password',
                'role': 'superadmin', 'department_id': 1
            },
            {
                'id': 2, 'username': 'eng_manager', 'phone': '+62-811-0000-002',
                'email': 'eng.manager@company.com', 'password': 'password',
                'role': 'manager', 'department_id': 1
            },
            {
                'id': 3, 'username': 'hr_manager', 'phone': '+62-811-0000-003',
                'email': 'hr.manager@company.com', 'password': 'password',
                'role': 'manager', 'department_id': 2
            },
            {
                'id': 4, 'username': 'budi', 'phone': '+62-811-0000-004',
                'email': 'budi@company.com', 'password': 'password',
                'role': 'employee', 'department_id': 1
            },
            {
                'id': 5, 'username': 'sari', 'phone': '+62-811-0000-005',
                'email': 'sari@company.com', 'password': 'password',
                'role': 'employee', 'department_id': 2
            }
        ]
        
        for user_data in users_data:
            user = User.query.filter_by(id=user_data['id']).first()
            if not user:
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    phone=user_data['phone'],
                    email=user_data['email'],
                    role=user_data['role'],
                    department_id=user_data['department_id'],
                    is_active=True
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"✅ Created user: {user.username} ({user.role})")
            else:
                print(f"⚠️  User already exists: {user.username}")
        
        db.session.commit()
        
        # Update department managers
        print("\n👔 Updating department managers...")
        dept1 = Department.query.get(1)
        dept1.manager_id = 2  # eng_manager
        dept2 = Department.query.get(2)
        dept2.manager_id = 3  # hr_manager
        db.session.commit()
        print("✅ Department managers updated")
        
        # Create Floors
        print("\n🏢 Creating floors...")
        floors_data = [
            {'id': 1, 'name': 'Lantai 10'},
            {'id': 2, 'name': 'Lantai 11'},
            {'id': 3, 'name': 'Lantai 12'},
            {'id': 4, 'name': 'Lantai 13'},
            {'id': 5, 'name': 'Lantai 14'}
        ]
        
        for floor_data in floors_data:
            floor = Floor.query.filter_by(id=floor_data['id']).first()
            if not floor:
                floor = Floor(
                    id=floor_data['id'],
                    name=floor_data['name']
                )
                db.session.add(floor)
                print(f"✅ Created floor: {floor.name}")
            else:
                print(f"⚠️  Floor already exists: {floor.name}")
        
        db.session.commit()
        
        # Create Spaces
        print("\n🚪 Creating spaces...")
        opening_hours = {
            'mon': {'start': '08:00', 'end': '18:00'},
            'tue': {'start': '08:00', 'end': '18:00'},
            'wed': {'start': '08:00', 'end': '18:00'},
            'thu': {'start': '08:00', 'end': '18:00'},
            'fri': {'start': '08:00', 'end': '18:00'},
            'sat': None,
            'sun': None
        }
        
        # Get available floor IDs for random assignment
        floor_ids = [1, 2, 3, 4, 5]
        
        spaces_data = [
            {
                'id': 1, 'name': 'Ruang Merapi', 'type': 'meeting_room',
                'capacity': 8, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 120, 'buffer_min': 15, 'status': 'available'
            },
            {
                'id': 2, 'name': 'Booth 1', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 3, 'name': 'Ruang Bromo', 'type': 'meeting_room',
                'capacity': 10, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 120, 'buffer_min': 15, 'status': 'in_maintenance'
            },
            {
                'id': 4, 'name': 'Ruang Semeru', 'type': 'meeting_room',
                'capacity': 12, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 180, 'buffer_min': 15, 'status': 'available'
            },
            {
                'id': 5, 'name': 'Booth 2', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 6, 'name': 'Booth 3', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 7, 'name': 'Booth 4', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 8, 'name': 'Ruang Rinjani', 'type': 'meeting_room',
                'capacity': 6, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 120, 'buffer_min': 10, 'status': 'available'
            },
            {
                'id': 9, 'name': 'Ruang Krakatau', 'type': 'meeting_room',
                'capacity': 15, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 240, 'buffer_min': 20, 'status': 'available'
            },
            {
                'id': 10, 'name': 'Booth 5', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 11, 'name': 'Booth 6', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 12, 'name': 'Ruang Merbabu', 'type': 'meeting_room',
                'capacity': 8, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 120, 'buffer_min': 15, 'status': 'available'
            },
            {
                'id': 13, 'name': 'Booth 7', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 14, 'name': 'Booth 8', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 15, 'name': 'Ruang Slamet', 'type': 'meeting_room',
                'capacity': 4, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 90, 'buffer_min': 10, 'status': 'available'
            },
            {
                'id': 16, 'name': 'Booth 9', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 17, 'name': 'Booth 10', 'type': 'hot_desk',
                'capacity': 1, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 60, 'buffer_min': 5, 'status': 'available'
            },
            {
                'id': 18, 'name': 'Ruang Arjuno', 'type': 'meeting_room',
                'capacity': 6, 'location': random.choice(floor_ids), 'opening_hours': opening_hours,
                'max_duration': 120, 'buffer_min': 10, 'status': 'available'
            }
        ]
        
        for space_data in spaces_data:
            space = Space.query.filter_by(id=space_data['id']).first()
            if not space:
                space = Space(**space_data)
                db.session.add(space)
                print(f"✅ Created space: {space.name} ({space.type}) - Floor ID: {space.location}")
            else:
                # Update existing space with random floor
                space.location = space_data['location']
                print(f"⚠️  Space already exists, updating floor: {space.name} - Floor ID: {space.location}")
        
        db.session.commit()
        
        # Create Amenities
        print("\n🛠️  Creating amenities...")
        amenities_data = [
            # Ruang Merapi (ID: 1)
            {'id': 1, 'space_id': 1, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 2, 'space_id': 1, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': 3, 'space_id': 1, 'name': 'Whiteboard', 'icon': 'whiteboard'},
            # Booth 1 (ID: 2)
            {'id': 4, 'space_id': 2, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 5, 'space_id': 2, 'name': 'AC', 'icon': 'ac'},
            # Ruang Bromo (ID: 3)
            {'id': 6, 'space_id': 3, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 7, 'space_id': 3, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': 8, 'space_id': 3, 'name': 'Whiteboard', 'icon': 'whiteboard'},
            # Ruang Semeru (ID: 4)
            {'id': 9, 'space_id': 4, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 10, 'space_id': 4, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': 11, 'space_id': 4, 'name': 'Whiteboard', 'icon': 'whiteboard'},
            {'id': 12, 'space_id': 4, 'name': 'Projector', 'icon': 'projector'},
            # Booth 2 (ID: 5)
            {'id': 13, 'space_id': 5, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 14, 'space_id': 5, 'name': 'AC', 'icon': 'ac'},
            # Booth 3 (ID: 6)
            {'id': 15, 'space_id': 6, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 16, 'space_id': 6, 'name': 'AC', 'icon': 'ac'},
            # Booth 4 (ID: 7)
            {'id': 17, 'space_id': 7, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 18, 'space_id': 7, 'name': 'AC', 'icon': 'ac'},
            # Ruang Rinjani (ID: 8)
            {'id': 19, 'space_id': 8, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 20, 'space_id': 8, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': 21, 'space_id': 8, 'name': 'Whiteboard', 'icon': 'whiteboard'},
            # Ruang Krakatau (ID: 9)
            {'id': 22, 'space_id': 9, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 23, 'space_id': 9, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': 24, 'space_id': 9, 'name': 'Whiteboard', 'icon': 'whiteboard'},
            {'id': 25, 'space_id': 9, 'name': 'Projector', 'icon': 'projector'},
            {'id': 26, 'space_id': 9, 'name': 'Video Conference', 'icon': 'video'},
            # Booth 5 (ID: 10)
            {'id': 27, 'space_id': 10, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 28, 'space_id': 10, 'name': 'AC', 'icon': 'ac'},
            # Booth 6 (ID: 11)
            {'id': 29, 'space_id': 11, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 30, 'space_id': 11, 'name': 'AC', 'icon': 'ac'},
            # Ruang Merbabu (ID: 12)
            {'id': 31, 'space_id': 12, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 32, 'space_id': 12, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': 33, 'space_id': 12, 'name': 'Whiteboard', 'icon': 'whiteboard'},
            # Booth 7 (ID: 13)
            {'id': 34, 'space_id': 13, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 35, 'space_id': 13, 'name': 'AC', 'icon': 'ac'},
            # Booth 8 (ID: 14)
            {'id': 36, 'space_id': 14, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 37, 'space_id': 14, 'name': 'AC', 'icon': 'ac'},
            # Ruang Slamet (ID: 15)
            {'id': 38, 'space_id': 15, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 39, 'space_id': 15, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': 40, 'space_id': 15, 'name': 'Whiteboard', 'icon': 'whiteboard'},
            # Booth 9 (ID: 16)
            {'id': 41, 'space_id': 16, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 42, 'space_id': 16, 'name': 'AC', 'icon': 'ac'},
            # Booth 10 (ID: 17)
            {'id': 43, 'space_id': 17, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 44, 'space_id': 17, 'name': 'AC', 'icon': 'ac'},
            # Ruang Arjuno (ID: 18)
            {'id': 45, 'space_id': 18, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': 46, 'space_id': 18, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': 47, 'space_id': 18, 'name': 'Whiteboard', 'icon': 'whiteboard'},
        ]
        
        for amenity_data in amenities_data:
            amenity = Amenity.query.filter_by(id=amenity_data['id']).first()
            if not amenity:
                amenity = Amenity(**amenity_data)
                db.session.add(amenity)
            else:
                print(f"⚠️  Amenity already exists: {amenity.name}")
        
        db.session.commit()
        print("✅ All amenities created")
        
        # Create Blackouts
        print("\n🚫 Creating blackouts...")
        blackouts_data = [
            {
                'id': 1, 'title': 'Libur Nasional',
                'start_at': datetime(2025, 4, 10, 0, 0, 0),
                'end_at': datetime(2025, 4, 11, 0, 0, 0),
                'created_by': 1
            }
        ]
        
        for blackout_data in blackouts_data:
            blackout = Blackout.query.filter_by(id=blackout_data['id']).first()
            if not blackout:
                blackout = Blackout(**blackout_data)
                db.session.add(blackout)
                print(f"✅ Created blackout: {blackout.title}")
            else:
                print(f"⚠️  Blackout already exists: {blackout.title}")
        
        db.session.commit()
        
        # Create Bookings
        print("\n📅 Creating bookings...")
        bookings_data = [
            {
                'id': 1, 'user_id': 4, 'space_id': 1, 'status': 'active',
                'start_at': datetime(2025, 1, 5, 3, 0, 0),
                'end_at': datetime(2025, 1, 5, 4, 30, 0),
                'buffer_min_snapshot': 15, 'max_duration_snapshot': 120,
                'checkin_code': 'CHK-1A2B3C4D',
                'code_valid_from': datetime(2025, 1, 5, 2, 45, 0),
                'code_valid_to': datetime(2025, 1, 5, 4, 45, 0),
                'checkin_at': None, 'checkout_at': None
            },
            {
                'id': 2, 'user_id': 5, 'space_id': 2, 'status': 'active',
                'start_at': datetime(2025, 1, 5, 2, 0, 0),
                'end_at': datetime(2025, 1, 5, 2, 30, 0),
                'buffer_min_snapshot': 5, 'max_duration_snapshot': 60,
                'checkin_code': 'CHK-9Z8Y7X6W',
                'code_valid_from': datetime(2025, 1, 5, 1, 45, 0),
                'code_valid_to': datetime(2025, 1, 5, 2, 45, 0),
                'checkin_at': datetime(2025, 1, 5, 2, 0, 30),
                'checkout_at': None
            },
            {
                'id': 3, 'user_id': 4, 'space_id': 1, 'status': 'cancelled',
                'start_at': datetime(2025, 1, 6, 6, 0, 0),
                'end_at': datetime(2025, 1, 6, 7, 0, 0),
                'buffer_min_snapshot': 15, 'max_duration_snapshot': 120,
                'checkin_code': 'CHK-CANCELLED',
                'code_valid_from': datetime(2025, 1, 6, 5, 45, 0),
                'code_valid_to': datetime(2025, 1, 6, 7, 15, 0),
                'checkin_at': None, 'checkout_at': None
            }
        ]
        
        for booking_data in bookings_data:
            booking = Booking.query.filter_by(id=booking_data['id']).first()
            if not booking:
                booking = Booking(**booking_data)
                db.session.add(booking)
                print(f"✅ Created booking: ID {booking.id} - User {booking.user_id}")
            else:
                print(f"⚠️  Booking already exists: ID {booking.id}")
        
        db.session.commit()
        
        print("\n✨ Database seeding completed!")
        print("\n📝 Summary:")
        print(f"   - Departments: {Department.query.count()}")
        print(f"   - Users: {User.query.count()}")
        print(f"   - Floors: {Floor.query.count()}")
        print(f"   - Spaces: {Space.query.count()}")
        print(f"   - Amenities: {Amenity.query.count()}")
        print(f"   - Blackouts: {Blackout.query.count()}")
        print(f"   - Bookings: {Booking.query.count()}")
        
        print("\n📝 Login credentials:")
        print("   Username: superadmin | Password: password (role: superadmin)")
        print("   Username: eng_manager | Password: password (role: manager)")
        print("   Username: hr_manager | Password: password (role: manager)")
        print("   Username: budi | Password: password (role: employee)")
        print("   Username: sari | Password: password (role: employee)")

if __name__ == '__main__':
    seed_data()
