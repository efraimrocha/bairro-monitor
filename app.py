from flask import Flask, render_template, redirect, request, flash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'

logado = False


@app.route("/")
def index():
    global logado
    logado = False
    return render_template("login.html")


@app.route('/admin')
def admin():
    if logado:
        with open('usuarios.json') as usuariosTemp:
            usuarios = json.load(usuariosTemp)
        return render_template('admin.html', usuarios=usuarios)
    else:
        return redirect('/')
    
@app.route('/home', methods=['GET', 'POST'])
def home():
    global logado
    if not logado:  # Se o usuário não estiver logado, redireciona para a página inicial
        return redirect('/')
    
    # Código para exibir e criar reports
    with open('reports.json') as reportsTemp:
        reports = json.load(reportsTemp)
    
    if request.method == 'POST':
        tema = request.form.get('tema')
        descricao = request.form.get('descricao')
        anexo = request.files['anexo']  # Arquivo do anexo

        # Criar um ID único para o report
        report_id = len(reports) + 1

        # Salvar o anexo em um diretório estático
        anexo_filename = f"{report_id}_{anexo.filename}"
        anexo.save(f"static/uploads/{anexo_filename}")

        # Criar o novo report
        novo_report = {
            "id": report_id,
            "tema": tema,
            "descricao": descricao,
            "anexo": anexo_filename
        }

        # Adicionar o novo report à lista
        reports.append(novo_report)

        # Salvar os reports atualizados no arquivo JSON
        with open('reports.json', 'w') as reportsTemp:
            json.dump(reports, reportsTemp, indent=4)

        flash(f"Report {report_id} criado com sucesso!")

    return render_template('home.html', reports=reports)

@app.route('/login', methods=['POST'])
def login():
    global logado
    
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    
    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)
    
    if nome == 'admin' and senha == 'admin':
        logado = True
        return redirect('/admin')
    
    for usuario in usuarios:
        if usuario['nome'] == nome and usuario['senha'] == senha:
            logado = True
            return redirect('/home')
    
    # Se o login falhar
    logado = False
    flash("Usuário não encontrado ou senha incorreta")
    return redirect('/')



@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    global logado
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    user = {
        "nome": nome,
        "senha": senha
    }

    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)

    usuarios.append(user)

    with open('usuarios.json', 'w') as gravarTemp:
        json.dump(usuarios, gravarTemp, indent=4)

    logado = True
    flash(f'Usuário {nome} cadastrado!')
    return redirect('/admin')


@app.route('/excluirUsuario', methods=['POST'])
def excluirUsuario():
    global logado
    logado = True
    usuario_nome = request.form.get('deletarUsuario')

    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)

    # Encontrar o usuário pelo nome e remover da lista
    usuarios = [usuario for usuario in usuarios if usuario['nome'] != usuario_nome]

    # Atualizar o arquivo JSON sem o usuário deletado
    with open('usuarios.json', 'w') as excluirUsuario:
        json.dump(usuarios, excluirUsuario, indent=4)

    flash(f'Usuário {usuario_nome} excluído com sucesso!')
    return redirect('/admin')

@app.route('/editarUsuario/<nome>', methods=['GET', 'POST'])
def editarUsuario(nome):
    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)

    # Procurar o usuário a ser editado
    usuario = next((user for user in usuarios if user['nome'] == nome), None)

    if request.method == 'POST':
        novo_nome = request.form.get('nome')
        nova_senha = request.form.get('senha')

        # Atualizar os dados do usuário
        if usuario:
            usuario['nome'] = novo_nome
            usuario['senha'] = nova_senha

        # Salvar as alterações no arquivo JSON
        with open('usuarios.json', 'w') as gravarTemp:
            json.dump(usuarios, gravarTemp, indent=4)

        flash(f'Usuário {novo_nome} atualizado com sucesso!')
        return redirect('/admin')

    return render_template('editar_usuario.html', usuario=usuario)



if __name__ == "__main__":
    app.run(debug=True)
