# Perbaikan untuk Broken Access Control
from flask import abort
from flask_login import current_user

@app.route('/designs/<int:design_id>')
def design(design_id):
    design = PCBDesign.query.get(design_id)
    if design.user_id != current_user.id:
        abort(403)  #Forbidden
    # ...

# Perbaikan untuk SQL Injection
from sqlalchemy import text

@app.route('/designs/<int:design_id>')
def design(design_id):
    query = text("SELECT * FROM pcb_designs WHERE id = :design_id")
    result = db.engine.execute(query, {"design_id": design_id})
    # ...
