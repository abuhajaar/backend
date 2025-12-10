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
from src.models.announcement import Announcement
from src.models.assignment import Assignment
from src.models.task import Task

def seed_data():
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Create Departments
        print("\n📁 Creating departments...")
        departments_data = [
            {
                'id': 1, 
                'name': 'Engineering', 
                'description': 'Responsible for product development, system architecture, and technical innovation',
                'manager_id': None
            },
            {
                'id': 2, 
                'name': 'People Ops', 
                'description': 'Manages recruitment, employee relations, training, and organizational development',
                'manager_id': None
            }
        ]
        
        for dept_data in departments_data:
            dept = Department.query.filter_by(id=dept_data['id']).first()
            if not dept:
                dept = Department(
                    id=dept_data['id'],
                    name=dept_data['name'],
                    description=dept_data['description'],
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
            {'id': 1, 'name': 'Lantai 1'},
            {'id': 2, 'name': 'Lantai 2'},
            {'id': 3, 'name': 'Lantai 3'}
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
        
        spaces_data = []
        space_id = 1
        
        # Lantai 1: 12 hot_desk, 3 meeting_room, 2 private_room
        # Hot Desks
        for i in range(1, 13):
            spaces_data.append({
                'id': space_id, 'name': f'Hot Desk 1.{i}', 'type': 'hot_desk',
                'capacity': 1, 'location': 1, 'opening_hours': opening_hours,
                'max_duration': 480, 'status': 'available'
            })
            space_id += 1
        
        # Meeting Rooms
        meeting_rooms_l1 = [
            {'name': 'Meeting Room 1.1', 'capacity': 6},
            {'name': 'Meeting Room 1.2', 'capacity': 8},
            {'name': 'Meeting Room 1.3', 'capacity': 10}
        ]
        for mr in meeting_rooms_l1:
            spaces_data.append({
                'id': space_id, 'name': mr['name'], 'type': 'meeting_room',
                'capacity': mr['capacity'], 'location': 1, 'opening_hours': opening_hours,
                'max_duration': 180, 'status': 'available'
            })
            space_id += 1
        
        # Private Rooms
        for i in range(1, 3):
            spaces_data.append({
                'id': space_id, 'name': f'Private Room 1.{i}', 'type': 'private_room',
                'capacity': 2, 'location': 1, 'opening_hours': opening_hours,
                'max_duration': 480, 'status': 'available'
            })
            space_id += 1
        
        # Lantai 2: 8 hot_desk, 3 meeting_room, 1 private_room
        # Hot Desks
        for i in range(1, 9):
            spaces_data.append({
                'id': space_id, 'name': f'Hot Desk 2.{i}', 'type': 'hot_desk',
                'capacity': 1, 'location': 2, 'opening_hours': opening_hours,
                'max_duration': 480, 'status': 'available'
            })
            space_id += 1
        
        # Meeting Rooms
        meeting_rooms_l2 = [
            {'name': 'Meeting Room 2.1', 'capacity': 8},
            {'name': 'Meeting Room 2.2', 'capacity': 10},
            {'name': 'Meeting Room 2.3', 'capacity': 12}
        ]
        for mr in meeting_rooms_l2:
            spaces_data.append({
                'id': space_id, 'name': mr['name'], 'type': 'meeting_room',
                'capacity': mr['capacity'], 'location': 2, 'opening_hours': opening_hours,
                'max_duration': 180, 'status': 'available'
            })
            space_id += 1
        
        # Private Room
        spaces_data.append({
            'id': space_id, 'name': 'Private Room 2.1', 'type': 'private_room',
            'capacity': 2, 'location': 2, 'opening_hours': opening_hours,
            'max_duration': 480, 'status': 'available'
        })
        space_id += 1
        
        # Lantai 3: 0 hot_desk, 2 meeting_room, 4 private_room
        # Meeting Rooms
        meeting_rooms_l3 = [
            {'name': 'Meeting Room 3.1', 'capacity': 15},
            {'name': 'Meeting Room 3.2', 'capacity': 20}
        ]
        for mr in meeting_rooms_l3:
            spaces_data.append({
                'id': space_id, 'name': mr['name'], 'type': 'meeting_room',
                'capacity': mr['capacity'], 'location': 3, 'opening_hours': opening_hours,
                'max_duration': 240, 'status': 'available'
            })
            space_id += 1
        
        # Private Rooms
        for i in range(1, 7):
            spaces_data.append({
                'id': space_id, 'name': f'Private Room 3.{i}', 'type': 'private_room',
                'capacity': 3, 'location': 3, 'opening_hours': opening_hours,
                'max_duration': 480, 'status': 'available'
            })
            space_id += 1
        
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
        amenities_data = []
        amenity_id = 1
        
        # Amenities for Lantai 1
        # Hot Desks (1-12) - basic amenities
        for space_id in range(1, 13):
            amenities_data.extend([
                {'id': amenity_id, 'space_id': space_id, 'name': 'Wi-Fi', 'icon': 'wifi'},
                {'id': amenity_id + 1, 'space_id': space_id, 'name': 'AC', 'icon': 'ac'}
            ])
            amenity_id += 2
        
        # Meeting Rooms (13-15) - standard meeting amenities
        for space_id in range(13, 16):
            amenities_data.extend([
                {'id': amenity_id, 'space_id': space_id, 'name': 'Wi-Fi', 'icon': 'wifi'},
                {'id': amenity_id + 1, 'space_id': space_id, 'name': 'Monitor', 'icon': 'monitor'},
                {'id': amenity_id + 2, 'space_id': space_id, 'name': 'Whiteboard', 'icon': 'whiteboard'},
                {'id': amenity_id + 3, 'space_id': space_id, 'name': 'AC', 'icon': 'ac'}
            ])
            amenity_id += 4
        
        # Private Rooms (16-17) - premium amenities
        for space_id in range(16, 18):
            amenities_data.extend([
                {'id': amenity_id, 'space_id': space_id, 'name': 'Wi-Fi', 'icon': 'wifi'},
                {'id': amenity_id + 1, 'space_id': space_id, 'name': 'Monitor', 'icon': 'monitor'},
                {'id': amenity_id + 2, 'space_id': space_id, 'name': 'Whiteboard', 'icon': 'whiteboard'},
                {'id': amenity_id + 3, 'space_id': space_id, 'name': 'AC', 'icon': 'ac'},
                {'id': amenity_id + 4, 'space_id': space_id, 'name': 'Printer', 'icon': 'printer'}
            ])
            amenity_id += 5
        
        # Amenities for Lantai 2
        # Hot Desks (18-25) - basic amenities
        for space_id in range(18, 26):
            amenities_data.extend([
                {'id': amenity_id, 'space_id': space_id, 'name': 'Wi-Fi', 'icon': 'wifi'},
                {'id': amenity_id + 1, 'space_id': space_id, 'name': 'AC', 'icon': 'ac'}
            ])
            amenity_id += 2
        
        # Meeting Rooms (26-28) - standard meeting amenities
        for space_id in range(26, 29):
            amenities_data.extend([
                {'id': amenity_id, 'space_id': space_id, 'name': 'Wi-Fi', 'icon': 'wifi'},
                {'id': amenity_id + 1, 'space_id': space_id, 'name': 'Monitor', 'icon': 'monitor'},
                {'id': amenity_id + 2, 'space_id': space_id, 'name': 'Whiteboard', 'icon': 'whiteboard'},
                {'id': amenity_id + 3, 'space_id': space_id, 'name': 'Projector', 'icon': 'projector'},
                {'id': amenity_id + 4, 'space_id': space_id, 'name': 'AC', 'icon': 'ac'}
            ])
            amenity_id += 5
        
        # Private Room (29) - premium amenities
        amenities_data.extend([
            {'id': amenity_id, 'space_id': 29, 'name': 'Wi-Fi', 'icon': 'wifi'},
            {'id': amenity_id + 1, 'space_id': 29, 'name': 'Monitor', 'icon': 'monitor'},
            {'id': amenity_id + 2, 'space_id': 29, 'name': 'Whiteboard', 'icon': 'whiteboard'},
            {'id': amenity_id + 3, 'space_id': 29, 'name': 'AC', 'icon': 'ac'},
            {'id': amenity_id + 4, 'space_id': 29, 'name': 'Printer', 'icon': 'printer'}
        ])
        amenity_id += 5
        
        # Amenities for Lantai 3
        # Meeting Rooms (30-31) - executive meeting amenities
        for space_id in range(30, 32):
            amenities_data.extend([
                {'id': amenity_id, 'space_id': space_id, 'name': 'Wi-Fi', 'icon': 'wifi'},
                {'id': amenity_id + 1, 'space_id': space_id, 'name': 'Monitor', 'icon': 'monitor'},
                {'id': amenity_id + 2, 'space_id': space_id, 'name': 'Whiteboard', 'icon': 'whiteboard'},
                {'id': amenity_id + 3, 'space_id': space_id, 'name': 'Projector', 'icon': 'projector'},
                {'id': amenity_id + 4, 'space_id': space_id, 'name': 'AC', 'icon': 'ac'},
                {'id': amenity_id + 5, 'space_id': space_id, 'name': 'Video Conference', 'icon': 'video'}
            ])
            amenity_id += 6
        
        # Private Rooms (32-37) - executive amenities
        for space_id in range(32, 38):
            amenities_data.extend([
                {'id': amenity_id, 'space_id': space_id, 'name': 'Wi-Fi', 'icon': 'wifi'},
                {'id': amenity_id + 1, 'space_id': space_id, 'name': 'Monitor', 'icon': 'monitor'},
                {'id': amenity_id + 2, 'space_id': space_id, 'name': 'Whiteboard', 'icon': 'whiteboard'},
                {'id': amenity_id + 3, 'space_id': space_id, 'name': 'AC', 'icon': 'ac'},
                {'id': amenity_id + 4, 'space_id': space_id, 'name': 'Printer', 'icon': 'printer'},
                {'id': amenity_id + 5, 'space_id': space_id, 'name': 'Coffee Machine', 'icon': 'coffee'}
            ])
            amenity_id += 6
        
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
                'id': 1, 
                'title': 'Hari Raya Idul Fitri',
                'description': 'National holiday celebrating the end of Ramadan. All office spaces are closed.',
                'start_at': datetime(2025, 4, 10, 0, 0, 0),
                'end_at': datetime(2025, 4, 11, 23, 59, 59),
                'created_by': 1
            },
            {
                'id': 2, 
                'title': 'Independence Day',
                'description': 'Indonesian Independence Day celebration. All facilities will be closed for the national holiday.',
                'start_at': datetime(2025, 8, 17, 0, 0, 0),
                'end_at': datetime(2025, 8, 17, 23, 59, 59),
                'created_by': 1
            },
            {
                'id': 3, 
                'title': 'Christmas Holiday',
                'description': 'Christmas celebration. Office closed for the holiday season.',
                'start_at': datetime(2025, 12, 25, 0, 0, 0),
                'end_at': datetime(2025, 12, 25, 23, 59, 59),
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
        bookings_data = []
        
        for booking_data in bookings_data:
            booking = Booking.query.filter_by(id=booking_data['id']).first()
            if not booking:
                booking = Booking(**booking_data)
                db.session.add(booking)
                print(f"✅ Created booking: ID {booking.id} - User {booking.user_id}")
            else:
                print(f"⚠️  Booking already exists: ID {booking.id}")
        
        db.session.commit()
        
        # Create Announcements
        print("\n📢 Creating announcements...")
        announcements_data = [
            {
                'id': 1,
                'title': 'Welcome to OpenBO!',
                'description': 'We are excited to introduce our new office booking system. Book your workspace easily and efficiently.',
                'created_by': 1,  # superadmin
                'department_id': None,  # Company-wide announcement
                'created_at': datetime(2025, 12, 1, 9, 0, 0)
            },
            {
                'id': 2,
                'title': 'Engineering Team Meeting',
                'description': 'All engineering team members are invited to the quarterly planning meeting on Friday at 2 PM in Meeting Room 3.1.',
                'created_by': 2,  # eng_manager
                'department_id': 1,  # Engineering department only
                'created_at': datetime(2025, 12, 5, 10, 30, 0)
            },
            {
                'id': 3,
                'title': 'New Workspace Guidelines',
                'description': 'Please ensure you check out from your workspace after use. Clean desk policy is now in effect.',
                'created_by': 1,  # superadmin
                'department_id': None,  # Company-wide
                'created_at': datetime(2025, 12, 7, 14, 0, 0)
            },
            {
                'id': 4,
                'title': 'HR Department Updates',
                'description': 'Important updates regarding employee benefits and year-end review process. Please check your email for details.',
                'created_by': 3,  # hr_manager
                'department_id': 2,  # People Ops department only
                'created_at': datetime(2025, 12, 8, 11, 15, 0)
            },
            {
                'id': 5,
                'title': 'Holiday Office Hours',
                'description': 'Office will operate on reduced hours during the holiday season. Check the blackout dates for office closures.',
                'created_by': 1,  # superadmin
                'department_id': None,  # Company-wide
                'created_at': datetime(2025, 12, 9, 8, 0, 0)
            }
        ]
        
        for announcement_data in announcements_data:
            announcement = Announcement.query.filter_by(id=announcement_data['id']).first()
            if not announcement:
                announcement = Announcement(**announcement_data)
                db.session.add(announcement)
                dept_text = f"Dept {announcement.department_id}" if announcement.department_id else "Company-wide"
                print(f"✅ Created announcement: {announcement.title} ({dept_text})")
            else:
                print(f"⚠️  Announcement already exists: {announcement.title}")
        
        db.session.commit()
        
        # Create Assignments
        print("\n📋 Creating assignments...")
        assignments_data = [
            {
                'id': 1,
                'title': 'Q4 Product Roadmap Planning',
                'description': 'Develop and finalize the product roadmap for Q4 2025. Include feature prioritization, timeline estimation, and resource allocation.',
                'created_by': 2,  # eng_manager
                'department_id': 1,  # Engineering
                'due_date': datetime(2025, 12, 20, 17, 0, 0),
                'created_at': datetime(2025, 12, 1, 9, 0, 0)
            },
            {
                'id': 2,
                'title': 'Employee Onboarding Process Review',
                'description': 'Review and update the employee onboarding process. Gather feedback from recent hires and improve documentation.',
                'created_by': 3,  # hr_manager
                'department_id': 2,  # People Ops
                'due_date': datetime(2025, 12, 15, 17, 0, 0),
                'created_at': datetime(2025, 12, 2, 10, 0, 0)
            },
            {
                'id': 3,
                'title': 'Code Review Best Practices Workshop',
                'description': 'Organize and conduct a workshop on code review best practices. Prepare presentation materials and practical exercises.',
                'created_by': 2,  # eng_manager
                'department_id': 1,  # Engineering
                'due_date': datetime(2025, 12, 18, 14, 0, 0),
                'created_at': datetime(2025, 12, 5, 11, 30, 0)
            }
        ]
        
        for assignment_data in assignments_data:
            assignment = Assignment.query.filter_by(id=assignment_data['id']).first()
            if not assignment:
                assignment = Assignment(**assignment_data)
                db.session.add(assignment)
                print(f"✅ Created assignment: {assignment.title} (Dept {assignment.department_id})")
            else:
                print(f"⚠️  Assignment already exists: {assignment.title}")
        
        db.session.commit()
        
        # Create Tasks
        print("\n✅ Creating tasks...")
        tasks_data = [
            # Tasks for Assignment 1 (Q4 Product Roadmap)
            {
                'id': 1,
                'title': 'Research competitor features',
                'priority': 'high',
                'assignment_id': 1,
                'user_id': 4,  # budi
                'is_done': True
            },
            {
                'id': 2,
                'title': 'Draft feature prioritization matrix',
                'priority': 'high',
                'assignment_id': 1,
                'user_id': 4,  # budi
                'is_done': False
            },
            {
                'id': 3,
                'title': 'Create timeline estimates',
                'priority': 'medium',
                'assignment_id': 1,
                'user_id': 4,  # budi
                'is_done': False
            },
            # Tasks for Assignment 2 (Onboarding Review)
            {
                'id': 4,
                'title': 'Survey recent hires',
                'priority': 'high',
                'assignment_id': 2,
                'user_id': 5,  # sari
                'is_done': True
            },
            {
                'id': 5,
                'title': 'Analyze feedback data',
                'priority': 'medium',
                'assignment_id': 2,
                'user_id': 5,  # sari
                'is_done': True
            },
            {
                'id': 6,
                'title': 'Update onboarding documentation',
                'priority': 'high',
                'assignment_id': 2,
                'user_id': 5,  # sari
                'is_done': False
            },
            # Tasks for Assignment 3 (Workshop)
            {
                'id': 7,
                'title': 'Prepare presentation slides',
                'priority': 'high',
                'assignment_id': 3,
                'user_id': 4,  # budi
                'is_done': False
            },
            {
                'id': 8,
                'title': 'Create hands-on exercises',
                'priority': 'medium',
                'assignment_id': 3,
                'user_id': 4,  # budi
                'is_done': False
            },
            {
                'id': 9,
                'title': 'Book meeting room',
                'priority': 'low',
                'assignment_id': 3,
                'user_id': 4,  # budi
                'is_done': True
            }
        ]
        
        for task_data in tasks_data:
            task = Task.query.filter_by(id=task_data['id']).first()
            if not task:
                task = Task(**task_data)
                db.session.add(task)
                status = "✓ Done" if task.is_done else "○ Pending"
                print(f"✅ Created task: {task.title} [{status}] (User {task.user_id})")
            else:
                print(f"⚠️  Task already exists: {task.title}")
        
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
        print(f"   - Announcements: {Announcement.query.count()}")
        print(f"   - Assignments: {Assignment.query.count()}")
        print(f"   - Tasks: {Task.query.count()}")
        
        print("\n📝 Login credentials:")
        print("   Username: superadmin | Password: password (role: superadmin)")
        print("   Username: eng_manager | Password: password (role: manager)")
        print("   Username: hr_manager | Password: password (role: manager)")
        print("   Username: budi | Password: password (role: employee)")
        print("   Username: sari | Password: password (role: employee)")

if __name__ == '__main__':
    seed_data()
