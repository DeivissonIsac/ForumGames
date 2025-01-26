from forumgames import app, database, bcrypt
from flask import render_template, flash, request, redirect, url_for
from forumgames.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from forumgames.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template("home.html", posts=posts)

@app.route('/contato')
def contato():
    return render_template('contato.html')

@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)

@app.route('/login-registro', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criar = FormCriarConta()
    if 'submit_login' in request.form and form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.permancer_conectado.data)
            flash(f'Bem-vindo(a) {usuario.username.title()}', 'alert-success')
            parametro_next = request.args.get('next')
            if parametro_next:
                return redirect(parametro_next)
            else:
                return redirect(url_for('home'))
        else:
            flash('E-mail ou Senha inválidos', 'alert-danger')
    elif 'submit_criar_conta' in request.form and form_criar.validate_on_submit():
        usuario = Usuario(username=form_criar.username.data, email=form_criar.email.data, senha=bcrypt.generate_password_hash(form_criar.senha.data).decode('utf-8'))
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com {form_criar.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criar=form_criar)

@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f'Logout feito com sucesso.', 'alert-success')
    return redirect(url_for('home'))

@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil)

@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso','alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)

def salvar_imagem_perfil(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_imagem = nome + codigo + extensao

    diretorio = os.path.join(app.root_path, 'static/fotos_perfil', nome_imagem)

    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)

    imagem_reduzida.save(diretorio)
    return nome_imagem

def atualizar_jogos(form):
    lista_jogos = []
    for campo in form:
        if 'jogo_' in campo.name:
            if campo.data:
                lista_jogos.append(campo.label.text)
    lista_jogos = ';'.join(lista_jogos)
    if len(lista_jogos) == 0:
        lista_jogos = 'Nao Informado'
    return lista_jogos

@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.foto_perfil.data:
            imagem = salvar_imagem_perfil(form.foto_perfil.data)
            current_user.foto_perfil = imagem
        current_user.jogos = atualizar_jogos(form)
        database.session.commit()
        flash(f'Seu perfil foi atualizado.', 'alert-info')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)

@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post atualizado com sucesso.', 'alert-success')
            return redirect(url_for('exibir_post', post_id=post.id))
    else:
        form = None
    return render_template('post.html', post=post, form=form)

@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído com sucesso.', 'alert-info')
        return redirect(url_for('home'))
    else:
        flash('Você não tem permissão para essa ação.', 'alert-danger')
        return redirect(url_for('home'))


#render_template = renderizador de arquivos html
#url_for = substitui a rota pelo nome da função (ao inves de "/" é "home")
#request = mostrará qual submit estará na requisição
#flash = para exibir mensagens de alerta
#redirect = para redirencionar automaticamente para a página definida
#login_user, logout_user, current_user, login_required = gerenciar o login, o logout, usuario logado e onde o login é obrigatorio
