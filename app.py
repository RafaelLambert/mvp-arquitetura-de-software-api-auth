from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect,Flask,request,jsonify
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, User
from logger import logger
from schemas import UserSchema, UserUpdateSchema, UserSearchSchema, UserAuthLoginSchema, UserViewSchema, UserListSchema, UserDelSchema,\
                            show_users, show_user, show_users
from schemas.error import ErrorSchema
from flask_cors import CORS


info = Info(title="api-auth", version="0.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

if __name__ == '__main__':
    # Configuração da rede (host e porta)
    app.run(host='0.0.0.0', port=5003)

#definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
user_tag = Tag(name="User", description="Tela de cadastro, visualização e consulta do Aluno. Também é possível definir as notas de cada bimestre")

@app.get('/', tags=[home_tag])
def home():
    """"Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')

@app.post('/user', tags=[user_tag],
          responses={"200":UserViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_user(form: UserSchema):
    """Adiciona um novo User à base de dados

    Retorna uma representação dos users.
    """


    logger.info(f"Recebido: cpf={form.cpf}, password={form.password}, user_type={form.user_type}")

    try:
        user = User(
            cpf = form.cpf,
            password = form.password,
            user_type = form.user_type
        )
            
        # criando conexão com a base
        session = Session()
        logger.warning(session)

        # adicionando user
        session.add(user)
        logger.warning(user)

        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.warning(f"Adicionado usuário de cpf: '{user.cpf}'")
        return show_user(user), 200

    except ValueError as e:
        # Captura erro de validação do CPF ou senha
        error_msg = str(e)
        logger.warning(f"Erro ao adicionar usuário '{form.cpf}': {error_msg}")
        return {"message": error_msg}, 400
    
    except IntegrityError as e:
        # como a duplicidade do cpf é a provável razão do IntegrityError
        error_msg = "usuário de mesmo cpf já salvo na base :/"
        logger.warning(f"Erro ao adicionar usuário '{user.cpf}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo usuário :/"
        logger.warning(f"Erro ao adicionar usuário '{user.cpf}', {error_msg}")
        return {"message": error_msg}, 400

@app.get('/users', tags=[user_tag],
          responses={"200":UserListSchema, "409": ErrorSchema, "400": ErrorSchema})
def get_users():
    """Faz a busca por todos os Users cadastrados

    Retorna uma representação da listagem de users.
    """
    logger.debug(f"Coletando users")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    users = session.query(User).all()

    if not users:
        # se não há usuários cadastrados
        return {"users": []}, 200
    else:
        logger.debug(f"%d usuários econtrados" % len(users))
        # retorna a representação do user
        print(users)
        return show_users(users), 200
    
@app.get('/user', tags=[user_tag],
         responses={"200": UserViewSchema, "404": ErrorSchema})
def get_user(query: UserSearchSchema):
    """Faz a busca por um User a partir do id do user

    Retorna uma representação dos users.
    """
    user_cpf = query.cpf
    logger.debug(f"Coletando dados sobre user #{user_cpf}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    user = session.query(User).filter(User.cpf == user_cpf).first()

    if not user:
        # se o user não foi encontrado
        error_msg = "User não encontrado na base :/"
        logger.warning(f"Erro ao buscar user '{user_cpf}', {error_msg}")
        return {"message": error_msg}, 404
    else:
        logger.debug(f"User econtrado: '{user.cpf}'")
        # retorna a representação de user
        return show_user(user), 200
    
@app.delete('/user', tags=[user_tag],
            responses={"200": UserViewSchema,"404": ErrorSchema})    
def del_user(query: UserSearchSchema):
    """Deleta um usuário a partir do cpf de produto informado

    Retorna uma mensagem de confirmação da remoção.
    """
    user_cpf = unquote(unquote(query.cpf))
    print(user_cpf)
    logger.debug(f"Deletando dados sobre user #{user_cpf}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(User).filter(User.cpf == user_cpf).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado user #{user_cpf}")
        return {"message": "User removido", "cpf": user_cpf}
    else:
        # se o produto não foi encontrado
        error_msg = "User não encontrado na base :/"
        logger.warning(f"Erro ao deletar user #'{user_cpf}', {error_msg}")
        return {"message": error_msg}, 404

@app.put('/user', tags=[user_tag],
         responses={"200": UserViewSchema, "404": ErrorSchema, "400": ErrorSchema})
def update_user(query: UserSearchSchema, form: UserUpdateSchema):
    """Atualiza as informações de um usuário existente na base de dados

    Retorna a representação do usuário atualizado.
    """
    logger.info("")
    logger.info(query)
    logger.info(form)
    logger.info("")
    user_cpf = query.cpf
    logger.debug(f"Atualizando dados do user #{user_cpf}")
    
    # criando conexão com a base
    session = Session()
    try:

        # buscando o usuário pelo cpf
        user = session.query(User).filter(User.cpf == user_cpf).first()
        
        if not user:
            # se o usuário não for encontrado
            error_msg = "User não encontrado na base :/"
            logger.warning(f"Erro ao atualizar user '{user_cpf}', {error_msg}")
            return {"message": error_msg}, 404
        
        # atualizando os campos
        user.password = form.password
        
        # confirmando as alterações no banco
        session.commit()
        logger.debug(f"User atualizado: '{user.cpf}'")
        
        # retorna a representação do usuário atualizado
        return show_user(user), 200
    
    except Exception as e:
        # caso ocorra um erro inesperado
        error_msg = "Não foi possível atualizar o usuário :/"
        logger.error(f"Erro ao atualizar user '{user_cpf}', {error_msg}: {str(e)}")
        return {"message": error_msg}, 400
    finally:
        # encerrando a sessão
        session.close()

@app.post('/user/search', tags=[user_tag],
         responses={"200": UserViewSchema, "404": ErrorSchema, "400": ErrorSchema})
def search_user(form: UserSearchSchema):
    """Faz a busca por um User a partir do CPF usando método POST
    
    Esta rota utiliza POST em vez de GET para maior segurança com dados sensíveis como CPF.
    Retorna uma representação do user encontrado.
    """
    user_cpf = form.cpf
    logger.debug(f"Buscando user por CPF via POST: {user_cpf}")
    

    # criando conexão com a base
    session = Session()
    try:
        # fazendo a busca
        user = session.query(User).filter(User.cpf == user_cpf).first()

        if not user:
            # se o user não foi encontrado
            error_msg = "User não encontrado na base"
            logger.warning(f"Erro ao buscar user '{user_cpf}', {error_msg}")
            return {"message": error_msg}, 404
        
        logger.debug(f"User encontrado via POST: '{user.cpf}'")
        # retorna a representação de user (sem informações sensíveis)
        return show_user(user), 200
        
    except Exception as e:
        error_msg = "Erro interno ao processar a busca"
        logger.error(f"Erro ao buscar user '{user_cpf}': {str(e)}")
        return {"message": error_msg}, 500
    finally:
        session.close()

@app.post('/user/login', tags=[user_tag],
         responses={"200": UserViewSchema, "404": ErrorSchema, "400": ErrorSchema})
def login_user(form: UserAuthLoginSchema):
    """Faz a busca por um User a partir do CPF usando método POST
    
    Esta rota utiliza POST em vez de GET para maior segurança com dados sensíveis como CPF.
    Retorna uma representação do user encontrado.
    """
    print()
    print("Objeto form recebido:", form)
    
    user_cpf = form.cpf
    user_password = form.password

    logger.warning(f"Buscando user por CPF e senha  via POST 11: {user_cpf} <-:-> {user_password}")
    
    # Validação básica (opcional para MVP)
    if not user_cpf or not user_password:
        error_msg = "CPF e senha são obrigatórios"
        logger.warning(f"Erro ao buscar user, {error_msg}")
        return jsonify({"message": error_msg}), 400
        
    # criando conexão com a base
    session = Session()
    try:
        # fazendo a busca
        user = session.query(User).filter(User.cpf == user_cpf).first()

        if not user:
            # se o user não foi encontrado
            error_msg = "User não encontrado na base"
            logger.warning(f"Erro ao buscar user '{user_cpf}', {error_msg}")
            return jsonify({"message": error_msg}), 404
        
        # Verifica se usuário existe e senha corresponde (simples para MVP)
        if user.password != user_password:
            error_msg = "CPF ou senha incorretos"
            logger.warning(f"Erro ao logar, {error_msg}")
            return {"message": error_msg}, 401            
        
        logger.warning(f"cpf:{user.cpf}  - - senha:{user.password}")
        # retorna a representação de user (sem informações sensíveis)
        print(user)
        return jsonify(show_user(user)), 200
        
    except Exception as e:
        error_msg = "Erro interno ao processar a busca"
        logger.error(f"Erro ao buscar user '{user_cpf}': {str(e)}")
        return jsonify({"message": error_msg}), 500
    
    finally:
        print()
        session.close()   