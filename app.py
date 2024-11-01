from flask import Flask, redirect, render_template, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, SelectField, DateField
from wtforms.validators import Length, DataRequired
from config import config
from models import HistorySchema
from marshmallow import ValidationError
from datetime import datetime, timedelta
import os

app = Flask(__name__)

config_name = os.getenv("FLASK_ENV") or 'development'
app.config.from_object(config[config_name])

db = SQLAlchemy(app)

class RDM(db.Model):
    __tablename__ = "list_rdm"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    glpi = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum("RDM - Normal", "RDM - Padrão", "RDM - Emergencial", "SCRIPT"), default="RDM", nullable=False)
    status = db.Column(db.Enum("SUCESSO", "ERRO", "ROLLBACK"), default="SUCESSO", nullable=False)
    env = db.Column(db.Enum("PROD", "PREP", "HML", "DEV", "SBX", "CNT"), default="PROD", nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    
class RDMForm(FlaskForm):
    glpi = StringField("URL GLPI", validators=[Length(1, 255, "O campo deve conter entre 1 a 255 caracteres."), DataRequired("Campo obrigatório")], description="URL GLPI")
    type = SelectField("Tipo", validators=[DataRequired("Campo obrigatório")], choices=[('RDM - Normal', 'RDM - Normal'), ('RDM - Padrão', 'RDM - Padrão'), ('RDM - Emergencial', 'RDM - Emergencial'), ('SCRIPT', 'Script')])
    status = SelectField("Status", validators=[DataRequired("Campo obrigatório")], choices=[('SUCESSO', 'Sucesso'), ('ERRO', 'Erro'), ('ROLLBACK', 'Rollback')])
    env = SelectField("Ambiente", validators=[DataRequired("Campo obrigatório")], choices=[('PROD', 'PROD'), ('PREP', 'PREP'), ('HML', 'HML'), ('DEV', 'DEV'), ('SBX', 'SBX'), ('CNT', 'CNT')])
    datam = StringField("Data", validators=[DataRequired("Campo obrigatório")])
    submit = SubmitField("Enviar")

@app.route("/", methods=["GET", "POST"])
def index():
    form = RDMForm()
    if request.method == "POST":
        try:
            try:
                data = datetime.strptime(form.datam.data, "%d-%m-%Y")
            except Exception as e:
                flash(f"Data inválida", "danger")
                return redirect(url_for("index"))
            search = db.session.query(RDM).filter_by(glpi=form.glpi.data).first()
            if search:
                search.type = form.type.data
                search.status = form.status.data
                search.env = form.env.data
                search.date = data
                db.session.commit()
                flash("RDM Atualizada com sucesso", "success")
                return redirect(url_for("index"))
            else:
                add = RDM()
                add.glpi = form.glpi.data
                add.type = form.type.data
                add.status = form.status.data
                add.env = form.env.data
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
            elif validated_data['option'] == 'type_rdm_padrao':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.type == "RDM - Padrão").count()
            elif validated_data['option'] == 'type_rdm_normal':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.type == "RDM - Normal").count()
            elif validated_data['option'] == 'type_rdm_emergencial':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.type == "RDM - Emergencial").count()
            elif validated_data['option'] == 'type_script':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.type == "SCRIPT").count()
            elif validated_data['option'] == 'status_sucesso':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "SUCESSO").count() 
            elif validated_data['option'] == 'status_erro':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "ERRO").count() 
            elif validated_data['option'] == 'status_rollback':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "ROLLBACK").count() 
            elif validated_data['option'] == 'env_prod':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "PROD").count()
            elif validated_data['option'] == 'env_prep':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "PREP").count()
            elif validated_data['option'] == 'env_hml':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "HML").count()
            elif validated_data['option'] == 'env_dev':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "DEV").count()
            elif validated_data['option'] == 'env_sbx':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "SBX").count()
            elif validated_data['option'] == 'env_cnt':
                data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.env == "CNT").count()
            elif validated_data['option'] == 'list_sucesso' or validated_data['option'] == 'list_erro' or validated_data['option'] == 'list_rollback':
                lista = []
                if validated_data['option'] == 'list_sucesso':
                    data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "SUCESSO").all()
                elif validated_data['option'] == 'list_erro':
                    data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "ERRO").all()
                elif validated_data['option'] == 'list_rollback':
                    data = db.session.query(RDM).filter(RDM.date >= validated_data['start_date'], RDM.date <= validated_data['end_date'], RDM.status == "ROLLBACK").all()
                if data:
                    for d in data:
                        lista.append({
                            "glpi": d.glpi,
                            "type": d.type,
                            "status": d.status,
                            "env": d.env,
                            "date": d.date.strftime("%d/%m")
                        })
                    return jsonify(lista)
                else:
                    jsonify([])
            
        else:
            if validated_data['option'] == 'total':
                data = db.session.query(RDM).count()
            elif validated_data['option'] == 'type_rdm_padrao':
                data = db.session.query(RDM).filter(RDM.type == "RDM - Padrão").count()
            elif validated_data['option'] == 'type_rdm_normal':
                data = db.session.query(RDM).filter(RDM.type == "RDM - Normal").count()
            elif validated_data['option'] == 'type_rdm_emergencial':
                data = db.session.query(RDM).filter(RDM.type == "RDM - Emergencial").count()
            elif validated_data['option'] == 'type_script':
                data = db.session.query(RDM).filter(RDM.type == "SCRIPT").count()
            elif validated_data['option'] == 'status_sucesso':
                data = db.session.query(RDM).filter(RDM.status == "SUCESSO").count() 
            elif validated_data['option'] == 'status_erro':
                data = db.session.query(RDM).filter(RDM.status == "ERRO").count() 
            elif validated_data['option'] == 'status_rollback':
                data = db.session.query(RDM).filter(RDM.status == "ROLLBACK").count() 
            elif validated_data['option'] == 'env_prod':
                data = db.session.query(RDM).filter(RDM.env == "PROD").count()
            elif validated_data['option'] == 'env_prep':
                data = db.session.query(RDM).filter(RDM.env == "PREP").count()
            elif validated_data['option'] == 'env_hml':
                data = db.session.query(RDM).filter(RDM.env == "HML").count()
            elif validated_data['option'] == 'env_dev':
                data = db.session.query(RDM).filter(RDM.env == "DEV").count()
            elif validated_data['option'] == 'env_sbx':
                data = db.session.query(RDM).filter(RDM.env == "SBX").count()
            elif validated_data['option'] == 'env_cnt':
                data = db.session.query(RDM).filter(RDM.env == "CNT").count()
            elif validated_data['option'] == 'list_sucesso' or validated_data['option'] == 'list_erro' or validated_data['option'] == 'list_rollback':
                lista = []
                data_atual = datetime.now()
                data_ontem = (datetime.now() - timedelta(days=1))
                if validated_data['option'] == 'list_sucesso':
                    data = db.session.query(RDM).filter(RDM.date >= data_ontem, RDM.date <= data_atual, RDM.status == "SUCESSO").all()
                elif validated_data['option'] == 'list_erro':
                    data = db.session.query(RDM).filter(RDM.date >= data_ontem, RDM.date <= data_atual, RDM.status == "ERRO").all()
                elif validated_data['option'] == 'list_rollback':
                    data = db.session.query(RDM).filter(RDM.date >= data_ontem, RDM.date <= data_atual, RDM.status == "ROLLBACK").all()
                if data:
                    for d in data:
                        lista.append({
                            "glpi": d.glpi,
                            "type": d.type,
                            "status": d.status,
                            "env": d.env,
                            "date": d.date.strftime("%d/%m")
                        })
                    return jsonify(lista)
                else:
                    jsonify([])
        if data is None:
            return jsonify({"result": 0})
        else:
            return jsonify({"result": data})
        
    else:
        lista = RDM.query.order_by(desc(RDM.id)).all()
        return render_template("list.html", lista=lista)

if __name__ == "__main__":
    app.run(debug=True)