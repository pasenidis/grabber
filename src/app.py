from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from simpleflake import simpleflake
from datetime import datetime
import human_readable_ids
import traceback

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///developer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Links(db.Model):
    link_id = db.Column(db.String, primary_key = True)
    link_url = db.Column(db.String, nullable = False)
    link_regtime = db.Column(db.DateTime, default = datetime.utcnow())


    visits = db.relationship("Visits", backref="links")

    def __repr__(self):
        return f'<Link to {self.link_url} identified as {self.link_id} that was registered on {self.link_regtime}>'

class Visits(db.Model):
    visit_id = db.Column(db.String, primary_key = True)
    visit_ip = db.Column(db.String, nullable = False)
    visit_time = db.Column(db.DateTime, default = datetime.utcnow())

    link_id = db.Column(db.String, db.ForeignKey('links.link_id'))

    def __repr__(self):
        return f'<Visit from {self.visit_ip} identified as {self.visit_id} that was registered on {self.visit_time}, from parent {self.link_id} >'

@app.route('/')
def index():
    return jsonify({"message": "yo!"})

@app.route('/<string:link_id>')
def links(link_id):
    item = Links.query.get(link_id)

    current_visit = Visits(visit_id = simpleflake(), visit_ip = request.headers.get('CF-Connecting-IP'))

    try:
        db.session.add(current_visit)
        db.session.commit()
        return redirect(f"http://{item.link_url}")
    except:
        traceback.print_exc()
        return "ip append ooops.."

@app.route('/reg', methods = ['POST'])
def register():
    if request.method == "POST":

        req_data = request.form
        link_id = str(human_readable_ids.get_new_id()).replace(" ", "-")
        
        new_link = Links(link_id = link_id, link_url = req_data["link"])

        try:
            db.session.add(new_link)
            db.session.commit()
            return jsonify({"content": str(new_link)})
        except:
            traceback.print_exc()
            return "ooops.."

    if request.method == "GET":
        return "Method not allowed", 405

if __name__ == "__main__":
    app.run(debug = True)