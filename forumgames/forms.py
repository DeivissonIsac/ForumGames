from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField,PasswordField, SubmitField, BooleanField                   #importando os campos do form, do tipo: string, senha e botoes submit e booleano
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError             #importando validações dos campos: obrigatorio, e-mail, igual(senha) e tamanho
from forumgames.models import Usuario
from flask_login import current_user

class FormCriarConta(FlaskForm):
    username = StringField('Nome', validators=[DataRequired(), Length(3, 20)])
    email = StringField('E-mail', validators=[DataRequired(), Email(message='O e-mail é inválido.')])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmar = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha', message='As senhas não são iguais.')])
    submit_criar_conta = SubmitField('Criar')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado, faça o login para continuar.')

class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(message='O e-mail é inválido.')])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    permancer_conectado = BooleanField('Permanecer Conectado')
    submit_login = SubmitField('Login')

class FormEditarPerfil(FlaskForm):
    username = StringField('Nome',validators=[DataRequired(), Length(3, 30)])
    email = StringField('E-mail', validators=[DataRequired(), Email(message='O e-mail é inválido.')])
    foto_perfil = FileField('Atualizar foto:', validators=[FileAllowed(['jpg', 'png'], message='Apenas arquivos JPG ou PNG.')])
    jogo_gta = BooleanField('GTA')
    jogo_cs2 = BooleanField('CS2')
    jogo_resident4 = BooleanField('RE4')
    jogo_valorant = BooleanField('VALORANT')
    jogo_fifa = BooleanField('FIFA25')
    jogo_pb = BooleanField('POINT BLANK')
    jogo_minecraft = BooleanField('MINECRAFT')
    submit_editar_perfil = SubmitField('Salvar')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('E-mail já cadastrado, escolha outro e-mail.')

class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(6, 120)])
    corpo = TextAreaField('Escreva seu Post', validators=[DataRequired()])
    submit_criar_post = SubmitField('Salvar Post')