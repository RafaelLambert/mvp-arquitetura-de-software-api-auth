from pydantic import BaseModel
from typing import  List
from model.user import User

class UserSchema(BaseModel):
    """
    Define como um novo user a ser inserido, deve ser representado
    """
    cpf:str = "123.456.789-00"     
    password:str = ""
    user_type:str = ""

class UserSearchSchema(BaseModel):
    """
    Define como deve ser a estrutura que representa a busca que será
    feita apenas com base no cpf do ususário
    """
    cpf:str = "123.456.789-00"    

class UserAuthLoginSchema(BaseModel):
    """
    Define como deve ser a estrutura que representa a busca que será
    feita apenas com base no cpf do ususário
    """
    cpf:str
    password:str
    
class UserUpdateSchema(BaseModel):
    """
    Define o schema para atualizar a senha de um usurário.
    """
    password:str 

def show_users(users:List[User]):
    """ 
    Retorna uma representação do user seguindo o schema definido em
    UserViewSchema.
    """
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "cpf":user.cpf,
            "password":user.password,
            "user_type":user.user_type
        })
    return {"users":result}

class UserViewSchema(BaseModel):
    """ Define como um User será retornado
    """
    id: int = 1
    cpf:str = "123.456.789-00"     
    password:str = "Abc123"
    user_type:str = "teacher"
    

class UserDelSchema(BaseModel):
    """
    Define como deve ser a estrutura do dado retornado após uma requisição
    de remoção.
    """

    message: str
    cpf: str
    
def show_user(user:User):
    """
    Retorna uma representação do user seguindo o schema definido em
    UserViewSchema.        
    """
    return {
        "id": user.id,
        "cpf":user.cpf,
        "password":user.password,
        "user_type":user.user_type
    }            

class UserListSchema(BaseModel):
    """
    Define como uma listagem de produtos será retornada.
    """
    usersList:List[UserViewSchema]