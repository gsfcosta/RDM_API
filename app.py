from flask import Flask, redirect, render_template, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, SelectField, DateField
from wtforms.validators import Length, DataRequired
from config import config
from models import HistorySchema
from marshmallow import ValidationError
from datetime import datetime
import os

app = Flask(__name__)

config_name = os.getenv("FLASK_ENV") or 'development'
app.config.from_object(config[config_name])

db = SQLAlchemy(app)

class RDM(db.Model):
    __tablename__ = "list_rdm"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    glpi = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum("RDM", "SCRIPT"), default="RDM", nullable=False)
    status = db.Column(db.Enum("SUCESSO", "ERRO", "ROLLBACK"), default="SUCESSO", nullable=False)
    env = db.Column(db.Enum("PROD", "PREP", "HML", "DEV", "SBX", "CNT"), default="PROD", nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    
class RDMForm(FlaskForm):
    glpi = StringField("URL GLPI", validators=[Length(1, 255, "O campo deve conter entre 1 a 255 caracteres."), DataRequired("Campo obrigatório")], description="URL GLPI")
    type = SelectField("Tipo", validators=[DataRequired("Campo obrigatório")], choices=[('RDM', 'RDM'), ('SCRIPT', 'Script')])
    status = SelectField("Status", validators=[DataRequired("Campo obrigatório")], choices=[('SUCESSO', 'Sucesso'), ('ERRO', 'Erro'), ('ROLLBACK', 'Rollback')])
    env = SelectField("Ambiente", validators=[DataRequired("Campo obrigatório")], choices=[('PROD', 'PROD'), ('PREP', 'PREP'), ('HML', 'HML'), ('DEV', 'DEV'), ('SBX', 'SBX'), ('CNT', 'CNT')])
    datam = StringField("Data", validators=[DataRequired("Campo obrigatório")])
    submit = SubmitField("Enviar")

@app.route("/", methods=["GET", "POST"])
def index():
    form = RDMForm()
    if request.method == "POST":
        try:
            add = RDM()
            add.glpi = form.glpi.data
            add.type = form.type.data
            add.status = form.status.data
            add.env = form.env.data
            try:
                data = datetime.strptime(form.datam.data, "%d-%m-%Y")
            except Exception as e:
                flash(f"Data inválida", "danger")
                return redirect(url_for("index"))
            add.date = data
            db.session.add(add)
            db.session.commit()
            flash("RDM Adicionada com sucesso", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"{e}", "danger")
            return redirect(url_for("index"))
    else:
        return render_template("index.html", form=form)

@app.route("/list", methods=["GET", "POST"])
def list_rdm():
    if request.method == "POST":
        try:
            json_data = request.get_json()
            schema = HistorySchema()
            validated_data = schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 400
        
        validate_start_date = True if validated_data['start_date'] != 'all' else False
        validate_end_date = True if validated_data['end_date'] != 'all' else False
        data = None
        if validate_start_date and validate_end_date:
            if validated_data['option'] == 'total':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date']).count()
            elif validated_data['option'] == 'type_rdm':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.type == "RDM").count()
            elif validated_data['option'] == 'type_script':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.type == "SCRIPT").count()
            elif validated_data['option'] == 'status_sucesso':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "SUCESSO").count() 
            elif validated_data['option'] == 'status_erro':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "ERRO").count() 
            elif validated_data['option'] == 'status_rollback':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "ROLLBACK").count() 
            if validated_data['option'] == 'env_prod':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "PROD").count()
            if validated_data['option'] == 'env_prep':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "PREP").count()
            if validated_data['option'] == 'env_hml':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "HML").count()
            if validated_data['option'] == 'env_dev':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "DEV").count()
            if validated_data['option'] == 'env_sbx':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "SBX").count()
            if validated_data['option'] == 'env_cnt':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "CNT").count()
        else:
            if validated_data['option'] == 'total':
                data = db.session.query(RDM).count()
            elif validated_data['option'] == 'type_rdm':
                data = db.session.query(RDM).filter(RDM.type == "RDM").count()
            elif validated_data['option'] == 'type_script':
                data = db.session.query(RDM).filter(RDM.type == "SCRIPT").count()
            elif validated_data['option'] == 'status_sucesso':
                data = db.session.query(RDM).filter(RDM.status == "SUCESSO").count() 
            elif validated_data['option'] == 'status_erro':
                data = db.session.query(RDM).filter(RDM.status == "ERRO").count() 
            elif validated_data['option'] == 'status_rollback':
                data = db.session.query(RDM).filter(RDM.status == "ROLLBACK").count() 
            if validated_data['option'] == 'env_prod':
                data = db.session.query(RDM).filter(RDM.env == "PROD").count()
            if validated_data['option'] == 'env_prep':
                data = db.session.query(RDM).filter(RDM.env == "PREP").count()
            if validated_data['option'] == 'env_hml':
                data = db.session.query(RDM).filter(RDM.env == "HML").count()
            if validated_data['option'] == 'env_dev':
                data = db.session.query(RDM).filter(RDM.env == "DEV").count()
            if validated_data['option'] == 'env_sbx':
                data = db.session.query(RDM).filter(RDM.env == "SBX").count()
            if validated_data['option'] == 'env_cnt':
                data = db.session.query(RDM).filter(RDM.env == "CNT").count()
        if data is None:
            return jsonify({"result": 0})
        else:
            return jsonify({"result": data})
        
    else:
        lista = RDM.query.all()
        return render_template("list.html", lista=lista)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')