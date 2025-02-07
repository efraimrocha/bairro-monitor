from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Simulando um banco de dados em memória (use um banco real depois)
usuarios = [
    {"id": 1, "nome": "Efraim", "senha": "123456"},
    {"id": 2, "nome": "Admin", "senha": "adminpass"}
]

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/editar_usuario')
def editar_usuario():
    return render_template('editar_usuario.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# ===========================
# ROTAS PARA USUÁRIOS (API)
# ===========================

# Retorna todos os usuários
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    return jsonify(usuarios)

# Retorna um usuário específico pelo ID
@app.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    usuario = next((u for u in usuarios if u["id"] == id), None)
    return jsonify(usuario) if usuario else ('Usuário não encontrado', 404)

# Adiciona um novo usuário
@app.route('/usuarios', methods=['POST'])
def create_usuario():
    novo_usuario = request.json
    novo_usuario["id"] = len(usuarios) + 1
    usuarios.append(novo_usuario)
    return jsonify(novo_usuario), 201

# Atualiza um usuário pelo ID
@app.route('/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    usuario = next((u for u in usuarios if u["id"] == id), None)
    if not usuario:
        return ('Usuário não encontrado', 404)
    
    data = request.json
    usuario.update(data)
    return jsonify(usuario)

# Deleta um usuário pelo ID
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    global usuarios
    usuarios = [u for u in usuarios if u["id"] != id]
    return ('Usuário deletado', 200)

if __name__ == '__main__':
    app.run(debug=True)
