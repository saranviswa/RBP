from flask import current_app

class User:
    def create_user(self, first_name, last_name, email, login_id, password, contact_number,security_question, security_answer, db):
        user = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'login_id': login_id,
            'password': password,
            'contact_number': contact_number,
            'security_question': security_question,
            'security_answer': security_answer
        }
        return db.users.insert_one(user).inserted_id

class Movie():
    def create_movie(self, movie_name, total_tickets_allotted, theatre_name, avail_tickets, status, db):
        movie = {
            'movie_name': movie_name,
            'total_tickets_allotted': total_tickets_allotted,
            'theatre_name': theatre_name,
            'available_tickets': avail_tickets,
            'status': status
        }
        return db.movies.insert_one(movie).inserted_id

class Ticket():
    def add_ticket(self, email, movie_name, theatre_name, num_tickets, seat_number, db):
        ticket = {
            'email': email,
            'movie_name': movie_name,
            'theatre_name': theatre_name,
            'num_tickets': num_tickets,
            'seat_number': seat_number,
        }
        return db.tickets.insert_one(ticket).inserted_id