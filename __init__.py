#
# Arquivo Inicial de Desenvolvimento do Emissor 
#


# Bibliotecas
import biblioteca
import sys

emissNF = biblioteca.NFe()

# inializa Nota Fiscal
if emissNF.init_DLL() != 0:
    print('\nErro ao inicializar')
    sys.exit(1)

print('\nInitializado!')

emissNF.carregarXML()

ret_meth = emissNF.assinarNFE()
if ret_meth !=0:
    print('\nErro ao assinar NFE ERRO: ', ret_meth)
    sys.exit(1)
print('\nNota Fiscal Assinada')

ret_meth = emissNF.validar()
if ret_meth !=0:
    print('\nErro ao validar NFE, : ', ret_meth)
    sys.exit(1)
print('\nNota Fiscal Validada')

emissNF.guardaXML()

emissNF.finalizar_execucao()