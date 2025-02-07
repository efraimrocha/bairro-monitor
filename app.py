from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import logging
import os

# Configuração do logging
logging.basicConfig(level=logging.DEBUG)

# Criar a aplicação Flask
app = Flask(__name__)

# Definir a variável DATABASE_URL antes de usá-la
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://admin:admin123@localhost:5432/app_db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados
db = SQLAlchemy(app)
api = Api(app)

# Importar rotas depois de definir `app` e `db`
try:
    from routes import *
except ImportError as e:
    logging.error(f"Erro ao importar rotas: {e}")

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

# Modelo de Report
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tema = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    anexo = db.Column(db.String(200), nullable=True)

# Comando CLI para criar o banco de dados
@app.cli.command("criar-banco")
def criar_banco():
    """Cria o banco de dados."""
    with app.app_context():
        db.create_all()
    print("Banco de dados criado!")

# Recurso para gerenciar usuários
class UsuarioResource(Resource):
    def get(self, usuario_id=None):
        if usuario_id:
            usuario = Usuario.query.get(usuario_id)
            if usuario:
                return {"id": usuario.id, "nome": usuario.nome}
            return {"mensagem": "Usuário não encontrado"}, 404
        usuarios = Usuario.query.all()
        return [{"id": u.id, "nome": u.nome} for u in usuarios]

    def post(self):
        dados = request.get_json()
        nome = dados.get('nome')
        senha = dados.get('senha')

        if not nome or not senha:
            return {"mensagem": "Nome e senha são obrigatórios"}, 400

        if Usuario.query.filter_by(nome=nome).first():
            return {"mensagem": "Usuário já existe!"}, 400

        try:
            novo_usuario = Usuario(nome=nome, senha=senha)
            db.session.add(novo_usuario)
            db.session.commit()
            return {"mensagem": f"Usuário {nome} cadastrado!", "id": novo_usuario.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"mensagem": "Erro ao cadastrar usuário", "erro": str(e)}, 500

    def put(self, usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return {"mensagem": "Usuário não encontrado"}, 404

        dados = request.get_json()
        usuario.nome = dados.get('nome', usuario.nome)
        usuario.senha = dados.get('senha', usuario.senha)
        db.session.commit()

        return {"mensagem": f"Usuário {usuario.nome} atualizado!"}

    def delete(self, usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return {"mensagem": "Usuário não encontrado"}, 404

        db.session.delete(usuario)
        db.session.commit()

        return {"mensagem": f"Usuário {usuario.nome} excluído!"}

# Recurso para gerenciar reports
class ReportResource(Resource):
    def get(self, report_id=None):
        if report_id:
            report = Report.query.get(report_id)
            if report:
                return {"id": report.id, "tema": report.tema, "descricao": report.descricao, "anexo": report.anexo}
            return {"mensagem": "Report não encontrado"}, 404
        reports = Report.query.all()
        return [{"id": r.id, "tema": r.tema, "descricao": r.descricao, "anexo": r.anexo} for r in reports]

    def post(self):
        dados = request.get_json()
        tema = dados.get('tema')
        descricao = dados.get('descricao')
        anexo = dados.get('anexo', '')  # Permitir anexo opcional

        if not tema or not descricao:
            return {"mensagem": "Tema e descrição são obrigatórios"}, 400

        novo_report = Report(tema=tema, descricao=descricao, anexo=anexo)
        db.session.add(novo_report)
        db.session.commit()

        return {"mensagem": f"Report {tema} criado!", "id": novo_report.id}, 201

    def put(self, report_id):
        report = Report.query.get(report_id)
        if not report:
            return {"mensagem": "Report não encontrado"}, 404

        dados = request.get_json()
        report.tema = dados.get('tema', report.tema)
        report.descricao = dados.get('descricao', report.descricao)
        report.anexo = dados.get('anexo', report.anexo)
        db.session.commit()

        return {"mensagem": f"Report {report.tema} atualizado!"}

    def delete(self, report_id):
        report = Report.query.get(report_id)
        if not report:
            return {"mensagem": "Report não encontrado"}, 404

        db.session.delete(report)
        db.session.commit()

        return {"mensagem": f"Report {report.tema} excluído!"}

# Adicionando recursos à API
api.add_resource(UsuarioResource, '/usuarios', '/usuarios/<int:usuario_id>')
api.add_resource(ReportResource, '/reports', '/reports/<int:report_id>')

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
