import flask
import flask_restful
import requests
import json
import os

# Biblioteca ACbr
import biblioteca as acb

# Inicia a Biblioteca
emissor = acb.NFe()
if emissor.init_DLL() != 0:
    pass
    print("Erro intero ao inicializar a API,\n cheque o arquivo de configuração: NFeConfig.ini")    

api = flask.Flask(__name__)
postApi = flask_restful.Api(api)


@api.route('/', methods=['POST'])
def raiz():    
    os.system('cls')
    print('\n\n\n\n#-----------------------------------#')
    post_body = json.loads(flask.request.data)
    try:
        # Convert o post em um arquivo ini
        emissor.json_to_ini_file(post_body)
    except:
        return{
            "Message": "Erro ao processar POST"
        }         

    
    
    ret_meth = emissor.carregarXML()

    
    
    ret_meth = emissor.assinarNFE()
    if ret_meth !=0:
        return{"Message": "Erro ao assinar NFE"}
    
    ret_meth = emissor.validar()
    if ret_meth !=0:
        return{"Message": "Erro ao validar NFE"}
    
        # Guarda XML
    notaFiscal = emissor.guardaXML()

    # Efetuar Entrga 
    emissor.enviar_nota_fiscal()
    
    return{
        "Message": "Sucesso",
        "NF_XML": notaFiscal
    }



if __name__ == '__main__':
    os.system('cls')
    
    try:
        api.run(debug=True, host='0.0.0.0', port=5723)
    except:
        # Caso haja qualquer erro matar a execução da lib
        emissor.finalizar_execucao()