from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_bcrypt import Bcrypt
from models import db, User, Event, Task, EventResource, Budget, Expense, Participant

# Adjust the database URI as needed
engine = create_engine("sqlite:///instance/app.db")
Session = sessionmaker(bind=engine)
session = Session()


def seed_users():
    users = [
        User(
            username="john_doe",
            email="john@example.com",
            firstname="John",
            lastname="Doe",
            address="123 Main St",
            city="Anytown",
            country="Country",
            postal_code="12345",
            aboutme="Lorem ipsum dolor sit amet.",
            password="password1",
        ),
        User(
            username="jane_doe",
            email="jane@example.com",
            firstname="Jane",
            lastname="Doe",
            address="456 Elm St",
            city="Othertown",
            country="Country",
            postal_code="54321",
            aboutme="Consectetur adipiscing elit.",
            password="password1",
        ),
        User(
            username="alex_smith",
            email="alex@example.com",
            firstname="Alex",
            lastname="Smith",
            address="789 Pine St",
            city="Sometown",
            country="Country",
            postal_code="67890",
            aboutme="Sed do eiusmod tempor incididunt.",
            password="password1",
        ),
        User(
            username="linda_white",
            email="linda@example.com",
            firstname="Linda",
            lastname="White",
            address="101 Maple Ave",
            city="Newtown",
            country="Country",
            postal_code="98765",
            aboutme="Ut labore et dolore magna aliqua.",
            password="password1",
        ),
        User(
            username="david_brown",
            email="david@example.com",
            firstname="David",
            lastname="Brown",
            address="202 Oak St",
            city="Oldtown",
            country="Country",
            postal_code="24680",
            aboutme="Ut enim ad minim veniam.",
            password="password1",
        ),
    ]

    session.add_all(users)
    session.commit()


def seed_events():
    events = [
        Event(
            user_id=1,
            title="Tech Conference",
            date=datetime.now() + timedelta(days=30),
            time=datetime.now().time(),
            location="Conference Center",
            description="A conference about tech.",
            category="Professional",
        ),
        Event(
            user_id=2,
            title="Wedding",
            date=datetime.now() + timedelta(days=90),
            time=datetime.now().time(),
            location="Sunny Meadows",
            description="Celebrating love.",
            category="Personal",
        ),
        Event(
            user_id=3,
            title="Hackathon",
            date=datetime.now() + timedelta(days=60),
            time=datetime.now().time(),
            location="Tech Hub",
            description="Coding competition.",
            category="Professional",
        ),
        Event(
            user_id=4,
            title="Birthday Party",
            date=datetime.now() + timedelta(days=20),
            time=datetime.now().time(),
            location="John's House",
            description="John's 30th birthday.",
            category="Social",
        ),
        Event(
            user_id=5,
            title="Charity Run",
            date=datetime.now() + timedelta(days=45),
            time=datetime.now().time(),
            location="City Park",
            description="5k run for charity.",
            category="Social",
        ),
    ]
    session.add_all(events)
    session.commit()


def seed_tasks():
    tasks = [
        Task(
            event_id=1,
            assigned_to=1,
            title="Prepare Keynote Speech",
            description="Finalize the slides for the keynote speech.",
            deadline=datetime.now() + timedelta(days=10),
            priority="High",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=2,
            assigned_to=2,
            title="Book Catering Service",
            description="Confirm the menu and number of guests with the caterer.",
            deadline=datetime.now() + timedelta(days=20),
            priority="Medium",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=1,
            assigned_to=3,
            title="Venue Decoration",
            description="Design and approve the decoration plans for the venue.",
            deadline=datetime.now() + timedelta(days=15),
            priority="Medium",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=3,
            assigned_to=2,
            title="Hire Security",
            description="Hire security personnel for the event.",
            deadline=datetime.now() + timedelta(days=5),
            priority="High",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=4,
            assigned_to=4,
            title="Confirm Guest Speakers",
            description="Finalize the list of guest speakers and confirm their attendance.",
            deadline=datetime.now() + timedelta(days=30),
            priority="High",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=5,
            assigned_to=5,
            title="Print Event Materials",
            description="Design and print all necessary event materials.",
            deadline=datetime.now() + timedelta(days=7),
            priority="Low",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=2,
            assigned_to=1,
            title="Social Media Campaign",
            description="Launch a social media campaign to promote the event.",
            deadline=datetime.now() + timedelta(days=12),
            priority="Medium",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=3,
            assigned_to=3,
            title="Prepare Participant Packets",
            description="Prepare welcome packets for all participants.",
            deadline=datetime.now() + timedelta(days=14),
            priority="Medium",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=4,
            assigned_to=2,
            title="Arrange Transportation",
            description="Arrange transportation for guests arriving from out of town.",
            deadline=datetime.now() + timedelta(days=25),
            priority="Low",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=2,
            assigned_to=4,
            title="Finalize Event Schedule",
            description="Finalize and publish the schedule for the event.",
            deadline=datetime.now() + timedelta(days=18),
            priority="High",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=4,
            assigned_to=5,
            title="Coordinate Volunteers",
            description="Assign roles and responsibilities to volunteers.",
            deadline=datetime.now() + timedelta(days=3),
            priority="Medium",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=3,
            assigned_to=2,
            title="Setup Online Registration",
            description="Ensure the online registration portal is functional.",
            deadline=datetime.now() + timedelta(days=17),
            priority="High",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=4,
            assigned_to=1,
            title="Confirm Event Insurance",
            description="Confirm all necessary insurance policies for the event.",
            deadline=datetime.now() + timedelta(days=22),
            priority="Medium",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=5,
            assigned_to=4,
            title="Develop Event App",
            description="Develop and test the event mobile application.",
            deadline=datetime.now() + timedelta(days=27),
            priority="Low",
            status="Not Started",
            dependency="None",
        ),
        Task(
            event_id=5,
            assigned_to=1,
            title="Plan Networking Activities",
            description="Plan and schedule networking activities for attendees.",
            deadline=datetime.now() + timedelta(days=19),
            priority="Medium",
            status="Not Started",
            dependency="None",
        ),
    ]
    session.add_all(tasks)
    session.commit()


def seed_resources():
    resources = [
        EventResource(
            event_id=1,
            name="Projector",
            type="Equipment",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=2,
            name="Venue",
            type="Location",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=3,
            name="Microphone",
            type="Equipment",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=4,
            name="Conference Room",
            type="Location",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=5,
            name="Laptop",
            type="Equipment",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=1,
            name="Outdoor Stage",
            type="Location",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=3,
            name="Video Camera",
            type="Equipment",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=4,
            name="Catering Services",
            type="Service",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=5,
            name="Chair Rental",
            type="Service",
            availability=True,
            reservation_date=datetime.now(),
        ),
        EventResource(
            event_id=5,
            name="Table Rental",
            type="Service",
            availability=True,
            reservation_date=datetime.now(),
        ),
    ]
    session.add_all(resources)
    session.commit()


def seed_budgets():
    budgets = [
        Budget(event_id=1, allocated_budget=10000.00),
        Budget(event_id=1, allocated_budget=12000.00),
        Budget(event_id=2, allocated_budget=20000.00),
        Budget(event_id=2, allocated_budget=22000.00),
        Budget(event_id=3, allocated_budget=15000.00),
        Budget(event_id=3, allocated_budget=17000.00),
        Budget(event_id=4, allocated_budget=25000.00),
        Budget(event_id=4, allocated_budget=27000.00),
        Budget(event_id=5, allocated_budget=18000.00),
        Budget(event_id=5, allocated_budget=20000.00),
    ]
    session.add_all(budgets)
    session.commit()


def seed_expenses():
    expenses = [
        Expense(
            budget_id=1,
            event_id=1,
            name="Sound System Rental",
            amount=1500.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=1,
            event_id=1,
            name="Catering Services",
            amount=2500.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=2,
            event_id=2,
            name="Decorations",
            amount=2000.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=2,
            event_id=2,
            name="Venue Booking",
            amount=5000.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=3,
            event_id=3,
            name="Marketing Materials",
            amount=1200.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=3,
            event_id=3,
            name="Guest Speaker Fees",
            amount=3000.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=4,
            event_id=4,
            name="Lighting Equipment",
            amount=1800.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=4,
            event_id=4,
            name="Security Services",
            amount=2200.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=5,
            event_id=5,
            name="Transportation",
            amount=1500.00,
            date=datetime.now(),
        ),
        Expense(
            budget_id=5,
            event_id=5,
            name="Accommodation",
            amount=4000.00,
            date=datetime.now(),
        ),
    ]
    session.add_all(expenses)
    session.commit()


def seed_participants():
    participants = [
        Participant(event_id=1, user_id=1, status="Confirmed", role="Speaker"),
        Participant(event_id=2, user_id=2, status="Confirmed", role="Guest"),
        Participant(event_id=1, user_id=3, status="Pending", role="Attendee"),
        Participant(event_id=3, user_id=4, status="Confirmed", role="Organizer"),
        Participant(event_id=2, user_id=5, status="Confirmed", role="Volunteer"),
    ]
    session.add_all(participants)
    session.commit()


def seed_all():
    seed_users()
    seed_events()
    seed_tasks()
    seed_resources()
    seed_budgets()
    seed_expenses()
    seed_participants()
    print("All data seeded successfully.")


if __name__ == "__main__":
    seed_all()
