#!/usr/bin/env python3
from flask import request
from flask_restful import Resource, marshal_with, fields
import os
from flask import Flask, request, make_response, jsonify, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    validators,
    IntegerField,
    DateTimeField,
    TextAreaField,
)
from wtforms.validators import DataRequired
from sqlalchemy.exc import IntegrityError

# from models import db, Event, Task, User
from models import db, Task, User, Event, Expense, Budget, Participant, EventResource
from flask_cors import CORS
from flask_restful import reqparse
import jwt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from functools import wraps


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = b"BM3\x1d\x16z!\x0e:\x8b&\xe6"
app.config["SECRET_KEY"] = "your_very_secret_key_here"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

db.init_app(app)
bcrypt = Bcrypt(app)
api = Api(app)
CORS(app)

migrate = Migrate(app, db)


class SignupResource(Resource):
    def post(self):
        # Directly access JSON data from the request
        data = request.json

        # Validate incoming data
        required_fields = [
            "username",
            "email",
            "password",
            "firstname",
            "lastname",
            "address",
            "city",
            "country",
            "postal_code",
            "aboutme",
        ]
        if not all(field in data for field in required_fields):
            return ({"error": "Missing required fields"}), 400

        # Check if the username or email already exists
        if (
            User.query.filter_by(username=data["username"]).first()
            or User.query.filter_by(email=data["email"]).first()
        ):
            return (
                (
                    {
                        "error": "Username or email already exists. Please choose a different one."
                    }
                ),
                400,
            )

        hashed_password = bcrypt.generate_password_hash(data["password"]).decode(
            "utf-8"
        )
        new_user = User(
            username=data["username"],
            email=data["email"],
            password=hashed_password,
            firstname=data["firstname"],
            lastname=data["lastname"],
            address=data["address"],
            city=data["city"],
            country=data["country"],
            postal_code=data["postal_code"],
            aboutme=data["aboutme"],
        )

        # Add the new user to the database
        db.session.add(new_user)

        try:
            # Commit the session to persist the changes
            db.session.commit()
            return ({"message": "User created successfully"}), 201
        except Exception as e:
            # Rollback the session in case of an error
            db.session.rollback()
            return ({"error": f"Failed to create user: {str(e)}"}), 500


class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "Missing username or password"}, 400

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
        else:
            return {"error": "Invalid username or password"}, 401


class LogoutResource(Resource):
    def delete(self):
        session["user_id"] = None
        return {"message": "Logout successful"}, 200


class PublicResource(Resource):
    def get(self):
        return "for public"


class AuthResource(Resource):
    @jwt_required()
    def get(self):
        return "JWT is verified. Welcome to your dashboard"


class CheckSessionResource(Resource):
    @jwt_required()
    def get(self):
        # Use the JWT identity to fetch the user details
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        if user:
            return user.to_dict(), 200
        return {"error": "User not found"}, 401


class AssignTaskResource(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON format"}), 400

        task_id = data.get("task_id")
        username = data.get("username")

        if not task_id or not username:
            return ({"error": "Missing required fields"}), 400

        # Query the user by username
        user = User.query.filter_by(username=username).first()

        if not user:
            return ({"error": "User not found"}), 404

        task = Task.query.get(task_id)

        if not task:
            return ({"error": "Task not found"}), 404

        task.assigned_to = user.id

        try:
            db.session.commit()
            return ({"message": "Task assigned successfully"}), 200
        except IntegrityError:
            db.session.rollback()
            return ({"error": "Database error"}), 500


event_fields = {
    "id": fields.Integer,
    "title": fields.String,
    "date": fields.DateTime,
    "time": fields.String,
    "location": fields.String,
    "description": fields.String,
    "category": fields.String,
}


class EventCreate(Resource):
    @marshal_with(event_fields)
    def post(self):
        data = request.get_json()

        # Parse date and time from the request JSON
        try:
            date = (
                datetime.strptime(data["date"], "%Y-%m-%d").date()
                if "date" in data
                else None
            )
            time = (
                datetime.strptime(data["time"], "%H:%M:%S").time()
                if "time" in data
                else None
            )
        except ValueError as e:
            return {"message": f"Invalid date or time format. {str(e)}"}, 400

        # Create new Event instance
        new_event = Event(
            title=data.get("title"),
            date=date,
            time=time,
            location=data.get("location"),
            description=data.get("description"),
            category=data.get("category"),
        )

        # Add to session and commit
        db.session.add(new_event)
        db.session.commit()

        return new_event, 201


class EventList(Resource):
    @marshal_with(event_fields)
    def get(self):
        events = Event.query.all()
        return events


class EventDetail(Resource):
    @marshal_with(event_fields)
    def get(self, event_id):
        event = Event.query.get_or_404(event_id)
        return event


class EventUpdate(Resource):
    def put(self, event_id):
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        if "date" in data:
            try:
                event.date = datetime.strptime(data["date"], "%Y-%m-%d")
            except ValueError:
                return {"message": "Incorrect date format. Please use YYYY-MM-DD."}, 400

        if "time" in data:
            try:
                event.time = datetime.strptime(data["time"], "%H:%M:%S").time()
                if event.date:
                    event.date = datetime.combine(event.date, event.time)
                else:
                    return {"message": "Date must be provided along with time."}, 400
            except ValueError:
                return {"message": "Incorrect time format. Please use HH:MM:SS."}, 400

        event.title = data.get("title", event.title)
        event.location = data.get("location", event.location)
        event.description = data.get("description", event.description)
        event.category = data.get("category", event.category)

        db.session.commit()
        return {"message": "Event updated successfully."}, 200


class EventDelete(Resource):
    def delete(self, event_id):
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return {"message": "Event deleted successfully."}, 200


class TaskCreate(Resource):
    def post(self, event_id):
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        deadline = datetime.strptime(data["deadline"], "%Y-%m-%dT%H:%M:%S")

        new_task = Task(
            event_id=event.id,
            title=data["title"],
            description=data.get("description", ""),
            deadline=deadline,
            priority=data.get("priority", "Medium"),
            status=data.get("status", "Pending"),
            assigned_to=data.get("assigned_to"),
            dependency=data.get("dependency", ""),
        )

        db.session.add(new_task)
        db.session.commit()
        return {"message": "Task added successfully to the event."}, 201


class TaskList(Resource):
    def get(self, event_id):
        tasks = Task.query.filter_by(event_id=event_id).all()
        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "priority": task.priority,
                "status": task.status,
                "assigned_to": task.assigned_to,
                "dependency": task.dependency,
            }
            for task in tasks
        ], 200


class TaskDetail(Resource):
    def get(self, event_id, task_id):
        task = Task.query.filter_by(event_id=event_id, id=task_id).first_or_404()
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "priority": task.priority,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "dependency": task.dependency,
        }, 200


class TaskUpdate(Resource):
    def put(self, event_id, task_id):
        task = Task.query.filter_by(event_id=event_id, id=task_id).first_or_404()
        data = request.get_json()

        if "deadline" in data:
            try:
                data["deadline"] = datetime.fromisoformat(data["deadline"])
            except ValueError:
                return {
                    "message": "Invalid deadline format. Please use ISO 8601 format."
                }, 400

        task.title = data.get("title", task.title)
        task.description = data.get("description", task.description)
        task.deadline = data.get("deadline", task.deadline)
        task.priority = data.get("priority", task.priority)
        task.status = data.get("status", task.status)
        task.assigned_to = data.get("assigned_to", task.assigned_to)
        task.dependency = data.get("dependency", task.dependency)

        db.session.commit()
        return {"message": "Task updated successfully."}, 200


class TaskDelete(Resource):
    def delete(self, event_id, task_id):
        task = Task.query.filter_by(event_id=event_id, id=task_id).first_or_404()
        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deleted successfully."}, 200


class ResourceCreate(Resource):
    def post(self, event_id):
        data = request.get_json()
        reservation_date = data.get("reservation_date")
        if reservation_date:
            reservation_date = datetime.strptime(reservation_date, "%Y-%m-%dT%H:%M:%S")

        new_resource = EventResource(
            event_id=event_id,
            name=data["name"],
            type=data["type"],
            availability=data.get("availability", True),
            reservation_date=reservation_date,
        )
        db.session.add(new_resource)
        db.session.commit()
        return {"message": "Resource allocated successfully to the event."}, 201


class ResourceList(Resource):
    def get(self, event_id):
        resources = EventResource.query.filter_by(event_id=event_id).all()
        return [
            {
                "id": resource.id,
                "name": resource.name,
                "type": resource.type,
                "availability": resource.availability,
                "reservation_date": (
                    resource.reservation_date.isoformat()
                    if resource.reservation_date
                    else None
                ),
            }
            for resource in resources
        ], 200


class ResourceDetail(Resource):
    def get(self, event_id, resource_id):
        resource = EventResource.query.filter_by(
            event_id=event_id, id=resource_id
        ).first_or_404()
        return {
            "id": resource.id,
            "name": resource.name,
            "type": resource.type,
            "availability": resource.availability,
            "reservation_date": (
                resource.reservation_date.isoformat()
                if resource.reservation_date
                else None
            ),
        }, 200


class ResourceUpdate(Resource):
    def put(self, event_id, resource_id):
        resource = EventResource.query.filter_by(
            event_id=event_id, id=resource_id
        ).first_or_404()
        data = request.get_json()
        reservation_date = data.get("reservation_date")
        if reservation_date:
            reservation_date = datetime.strptime(reservation_date, "%Y-%m-%dT%H:%M:%S")

        resource.name = data.get("name", resource.name)
        resource.type = data.get("type", resource.type)
        resource.availability = data.get("availability", resource.availability)
        resource.reservation_date = reservation_date

        db.session.commit()
        return {"message": "Resource updated successfully."}, 200


class ResourceDelete(Resource):
    def delete(self, event_id, resource_id):
        resource = EventResource.query.filter_by(
            event_id=event_id, id=resource_id
        ).first_or_404()
        db.session.delete(resource)
        db.session.commit()
        return {"message": "Resource removed successfully."}, 200


class ExpenseCreate(Resource):
    def post(self, event_id):
        data = request.get_json()
        date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        new_expense = Expense(
            event_id=event_id,
            name=data["name"],
            amount=data["amount"],
            date=date,
        )
        db.session.add(new_expense)
        db.session.commit()
        return {"message": "Expense recorded successfully."}, 201


class ExpenseList(Resource):
    def get(self, event_id):
        expenses = Expense.query.filter_by(event_id=event_id).all()
        return [
            {
                "id": expense.id,
                "name": expense.name,
                "amount": str(expense.amount),
                "date": expense.date.isoformat() if expense.date else None,
            }
            for expense in expenses
        ], 200


class ExpenseDetail(Resource):
    def get(self, event_id, expense_id):
        expense = Expense.query.filter_by(
            event_id=event_id, id=expense_id
        ).first_or_404()
        return {
            "id": expense.id,
            "name": expense.name,
            "amount": str(expense.amount),
            "date": expense.date.isoformat() if expense.date else None,
        }, 200


class ExpenseUpdate(Resource):
    def put(self, event_id, expense_id):
        expense = Expense.query.filter_by(
            event_id=event_id, id=expense_id
        ).first_or_404()
        data = request.get_json()
        date = datetime.strptime(data["date"], "%Y-%m-%d").date()

        expense.name = data.get("name", expense.name)
        expense.amount = data.get("amount", expense.amount)
        expense.date = date

        db.session.commit()
        return {"message": "Expense updated successfully."}, 200


class ExpenseDelete(Resource):
    def delete(self, event_id, expense_id):
        expense = Expense.query.filter_by(
            event_id=event_id, id=expense_id
        ).first_or_404()
        db.session.delete(expense)
        db.session.commit()
        return {"message": "Expense deleted successfully."}, 200


class UpdateTaskStatus(Resource):
    def put(self):
        data = request.get_json()
        if not data:
            return {"error": "Invalid JSON format"}, 400

        task_id = data.get("task_id")
        new_status = data.get("status")

        if not task_id or not new_status:
            return {"error": "Missing required fields"}, 400

        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404

        task.status = new_status
        try:
            db.session.commit()
            return {"message": "Task status updated successfully"}, 200
        except IntegrityError:
            db.session.rollback()
            return {"error": "Database error"}, 500


class CompleteTask(Resource):
    def put(self):
        data = request.get_json()
        if not data:
            return {"error": "Invalid JSON format"}, 400

        task_id = data.get("task_id")
        if not task_id:
            return {"error": "Missing required field: task_id"}, 400

        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404

        task.status = "Completed"
        try:
            db.session.commit()
            return {"message": "Task marked as completed successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": "Database error: " + str(e)}, 500


class CalculateTaskCompletion(Resource):
    def get(self, event_id):
        total_tasks = Task.query.filter_by(event_id=event_id).count()
        completed_tasks = Task.query.filter_by(
            event_id=event_id, status="Completed"
        ).count()

        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100
        else:
            completion_percentage = 0

        return {
            "event_id": event_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_percentage": completion_percentage,
        }, 200


class GenerateBudgetReport(Resource):
    def get(self, event_id):
        budget = Budget.query.filter_by(event_id=event_id).first()
        if not budget:
            return {"error": "Budget not found for the specified event"}, 404

        expenses = Expense.query.filter_by(budget_id=budget.id).all()
        total_spent_amount = sum(expense.amount for expense in expenses)
        remaining_budget = budget.allocated_budget - total_spent_amount

        return {
            "event_id": event_id,
            "allocated_budget": float(budget.allocated_budget),
            "total_spent_amount": float(total_spent_amount),
            "remaining_budget": float(remaining_budget),
        }, 200


class EventWithDetails(Resource):
    def get(self, event_id):
        # Fetch the event based on event_id
        event = Event.query.filter_by(id=event_id).first()

        if not event:
            return {"message": "Event not found"}, 404

        # Serialize the event data
        event_data = event.to_dict(
            rules=("-user.password",)
        )  # Exclude sensitive user info

        # Fetch and serialize associated data
        event_data["tasks"] = [
            task.to_dict() for task in Task.query.filter_by(event_id=event.id)
        ]
        event_data["resources"] = [
            resource.to_dict()
            for resource in EventResource.query.filter_by(event_id=event.id)
        ]
        event_data["budgets"] = [
            budget.to_dict() for budget in Budget.query.filter_by(event_id=event.id)
        ]
        event_data["expenses"] = [
            expense.to_dict() for expense in Expense.query.filter_by(event_id=event.id)
        ]
        event_data["participants"] = [
            participant.to_dict()
            for participant in Participant.query.filter_by(event_id=event.id)
        ]

        return jsonify(event_data)


api.add_resource(EventWithDetails, "/event-detail/<int:event_id>")
api.add_resource(UpdateTaskStatus, "/tasks/update-status")
api.add_resource(CompleteTask, "/tasks/complete")
api.add_resource(CalculateTaskCompletion, "/events/<int:event_id>/tasks/completion")
api.add_resource(GenerateBudgetReport, "/events/<int:event_id>/budget/report")


api.add_resource(ExpenseCreate, "/events/<int:event_id>/expenses")
api.add_resource(ExpenseList, "/events/<int:event_id>/expenses")
api.add_resource(ExpenseDetail, "/events/<int:event_id>/expenses/<int:expense_id>")
api.add_resource(ExpenseUpdate, "/events/<int:event_id>/expenses/<int:expense_id>")
api.add_resource(ExpenseDelete, "/events/<int:event_id>/expenses/<int:expense_id>")

api.add_resource(ResourceDetail, "/events/<int:event_id>/resources/<int:resource_id>")
api.add_resource(ResourceUpdate, "/events/<int:event_id>/resources/<int:resource_id>")
api.add_resource(ResourceDelete, "/events/<int:event_id>/resources/<int:resource_id>")

api.add_resource(TaskDelete, "/events/<int:event_id>/tasks/<int:task_id>")
api.add_resource(ResourceCreate, "/events/<int:event_id>/resources")
api.add_resource(ResourceList, "/events/<int:event_id>/resources")
api.add_resource(TaskList, "/events/<int:event_id>/tasks")
api.add_resource(TaskDetail, "/events/<int:event_id>/tasks/<int:task_id>")
api.add_resource(TaskUpdate, "/events/<int:event_id>/tasks/<int:task_id>")
api.add_resource(EventUpdate, "/events/<int:event_id>")
api.add_resource(EventDelete, "/events/<int:event_id>")
api.add_resource(TaskCreate, "/events/<int:event_id>/tasks")
api.add_resource(EventCreate, "/events")
api.add_resource(EventList, "/events")
api.add_resource(EventDetail, "/events/<int:event_id>")
api.add_resource(SignupResource, "/signup")
api.add_resource(LoginResource, "/login")
api.add_resource(LogoutResource, "/logout")
api.add_resource(PublicResource, "/public")
api.add_resource(AuthResource, "/auth")
api.add_resource(CheckSessionResource, "/checksession")
api.add_resource(AssignTaskResource, "/tasks/assign")


if __name__ == "__main__":
    app.run(debug=True)
