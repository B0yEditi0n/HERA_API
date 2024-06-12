# Bibliotecas
import ctypes
import os
import configparser

# Obtem a pasta do projeto
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

class NFe:
    # Caminhos de arquivos
    PATH_DLL                = os.path.abspath(os.path.join(os.sep, DIRETORIO_ATUAL, 'ACBrLib', 'ACBrNFe64.dll'))
    PATH_INI_CONFIG         = os.path.abspath(os.path.join(os.sep, DIRETORIO_ATUAL, 'ACBrLib', 'NFeConfig.ini'))
    PATH_LOG                = os.path.abspath(os.path.join(os.sep, DIRETORIO_ATUAL, "Log"))
    PATH_SCHEMA             = os.path.abspath(os.path.join(os.sep, DIRETORIO_ATUAL, "ACBrLib", "Schemas", "NFe"))
    INI_ACBR_NFE            = os.path.abspath(os.path.join(os.sep, DIRETORIO_ATUAL, "ACBrLib", 'ACBrNFeServicos.ini'))
    NFE_INI                 = os.path.join(os.sep, DIRETORIO_ATUAL, 'nfe.ini')

    # blbioteca
    cbr_lib = ctypes.cdll.LoadLibrary(PATH_DLL)
    eChaveCrypt = 'dn5fy#5215#sdh'

    def init_DLL(self):
        '''
            Incializa a DLL responsável por emitir NFe

            Args:
                int Returning : 
                    0    - Indica que o método foi inicializada corretamente.
                    -1   - Indica que a biblioteca não foi inicializada.
                    -10  - Indica que houve erro ao ler o arquivo INI.
                    -404 - DLL não encontrada")
        '''

        # cria o arquivo de log se não existir
        if not os.path.exists(self.PATH_LOG):
            os.makedirs(self.PATH_LOG) 

        #Verifica se a dll está no path indicado
        if not os.path.exists(self.PATH_DLL):
            return (-404)
        
        # inicializa a DLL
        init_retorno = self.cbr_lib.NFE_Inicializar(self.PATH_INI_CONFIG.encode("utf-8"), self.eChaveCrypt.encode("utf-8"))

        if init_retorno != 0:
            return (init_retorno)
        else:
            if self.configura_ini() == 0:
                return 0

        
    def configura_ini(self):
        '''
            Configura os parametros do arquivo INIT
            definindo algumas configurações de funcionamento
            da API

            Args:
                int Returning : 
                    0 - Sucesso na configuração
        '''
        #-----------------------------------------------------------------------------
        # Caio abreu de Souza 06.06.2024
        # a Documentação é horrivel de navegar, portanto não apage os links!

        # Configuração da Biblioteca    
        # consulte a documentação para mais detalhes
        # https://acbr.sourceforge.io/ACBrLib/Geral.html
        #-----------------------------------------------------------------------------
        
        # Resposta do Tipo JSON para texte
        self.escrever_ini("Principal", "TipoResposta", "2")
        # Codificação UTF-8
        self.escrever_ini("Principal", "CodificacaoResposta", "0")
        # Reposta tipo Paranoico (Retorno total)
        self.escrever_ini("Principal", "LogNivel", "4")
        # Path de armazenamento 
        self.escrever_ini("Principal", "LogPath", self.PATH_LOG)

        # Prenchimento referente a biblioteca
        # https://acbr.sourceforge.io/ACBrLib/ConfiguracoesdaBiblioteca16.html
        self.escrever_ini("NFe", "FormaEmissao", '0')
        self.escrever_ini("NFe", "SalvarGer", '0')
        self.escrever_ini("NFe", "ExibirErroSchema", '1')
        nf_dir = os.path.abspath(os.path.join(os.sep, DIRETORIO_ATUAL, 'xmlDir'))
        nf_ser = os.path.abspath(os.path.join(os.sep, DIRETORIO_ATUAL, 'ACBrLib', 'ACBrNFeServicos.ini'))
        self.escrever_ini("NFe", "PathSalvar", nf_dir)
        self.escrever_ini("NFe", "PathSchemas", self.PATH_SCHEMA)
        self.escrever_ini("NFe", "PathNFe", nf_dir)
        self.escrever_ini("NFe", "IniServicos", nf_ser)

        # Carregar Certificado
        # https://acbr.sourceforge.io/ACBrLib/DFe.html
        self.escrever_ini("DFe", "ArquivoPFX", os.path.abspath(os.path.join(os.sep, DIRETORIO_ATUAL, 'config', 'certificadoDigital', "server.pfx")))
        self.escrever_ini("DFe", "Senha", "Dh2022@@")
        self.escrever_ini("DFe", "SSLCryptLib", "1")
        self.escrever_ini("DFe", "SSLHttpLib", "3")
        self.escrever_ini("DFe", "SSLXmlSignLib", "4")

        self.escrever_ini("DANFE", "PathPDF", DIRETORIO_ATUAL)
        return 0
    
    def escrever_ini(self, sessao, chave, valor):
        '''
            Auxilia no preenchimento dos valores 
            para evitar extender codigo com conversões .utf(8)

            Args:
                Params:
                    sessao - valor que se encontra no ini como [sessao]
                    chave  - variável dentro da sessão a ser alteada
                    valor  - parametro de valor novo no ini
        '''
        self.cbr_lib.NFE_ConfigGravarValor(
            sessao.encode("utf-8"),
            chave.encode("utf-8"),
            valor.encode("utf-8")
        )
    
    def json_to_ini_file(self, json):
    
        '''
            Converte o dicionario em um arquivo ini NFE

             Args:
                Params:
                    json - Dicionario de Dados (Objeto json) com os dados do ini
                Return: 1 com diretório já concluido
                
        '''

        # dados de NFE
        ini_file = configparser.ConfigParser()
        # habilita sentive case nos campos
        ini_file.optionxform = str

        for s in json:
            itens_body = {}

            for iten in s['body']:
                itens_body[iten['key']] = iten['value']

            ini_file[s['session']] = itens_body
        try:
            with open('nfe.ini', 'w') as configfile:
                # remove espaços entre o = Key e o valor
                ini_file.write(configfile, space_around_delimiters=False)
                return 1
        except:
            print('caminho com problemas')

        
            
    def carregarXML(self):
        '''
            para preencher a nota fiscal é necessário cadastar alguns campos 
            no NFE.ini
            para evitar duvidas consulte o manual de layout
            https://www.confaz.fazenda.gov.br/legislacao/arquivo-manuais/moc7-anexo-i-leiaute-e-rv.pdf

        '''
        # Carrega uma NFE apartir do arquivo INI
        self.cbr_lib.NFE_CarregarINI(self.NFE_INI.encode('utf-8'))
        # os.remove(self.NFE_INI.encode('utf-8'))
        return 1

    

    def assinarNFE(self):
        return(self.cbr_lib.NFE_Assinar())

    def validar(self):
        return(self.cbr_lib.NFE_Validar())
    
    
    def guardaXML(self):
        '''
            Guarda a XML de Envio da NF criada

        '''

        # Parametros do tipo ponteiro para passar pra DLL
        esTamanho = ctypes.c_ulong(9048)
        sResposta = ctypes.create_string_buffer(9048)
                
        self.cbr_lib.NFE_ObterXml(0, sResposta, ctypes.byref(esTamanho))
        
        if esTamanho.value > len(sResposta.value):
            # Caso o tamanho de buffer seja insuficiente
            resposta = self.retornarMensagemCompleta(esTamanho.value)
        else:
            resposta = sResposta.value.decode("utf-8")
        return resposta

    def retornarMensagemCompleta(self, novo_Tamanho):
        '''
            Como as DLLs exigem passagem de ponteiros como parametro 
            o tamanho deve ser definido previamente. Este metódo será
            usado caso o tamanho da string de memória seja insuficiente.
            assim ele recaputrará a ultima saída e retornrá o valor total
            
            Args:
                Params:
                    int novo_Tamanho - é o tamanho que o retorno exige
                
                String Return - retornará a string completa do ultimo retorno

        '''

        DLL_resposta = ctypes.create_string_buffer(novo_Tamanho)
        DLL_tamanho = ctypes.c_ulong(novo_Tamanho)
        self.cbr_lib.NFE_UltimoRetorno(DLL_resposta, ctypes.byref(DLL_tamanho))

        return DLL_resposta.value.decode("utf-8")

    def enviar_nota_fiscal(self):
        """
            Método usado para enviar um lote de NFe para SEFAZ.
        """
        
        # Parametros do tipo ponteiro para passar pra DLL
        esTamanho = ctypes.c_ulong(9048)
        sResposta = ctypes.create_string_buffer(9048)

        self.cbr_lib.NFE_Enviar(
            1,     # Lote
            False, # Imprimir
            True,  # ASincrono
            False, # Zipado
            sResposta, ctypes.byref(esTamanho)
        )

        if esTamanho.value > len(sResposta.value):
            # Caso o tamanho de buffer seja insuficiente
            resposta = self.retornarMensagemCompleta(esTamanho.value)
        else:
            resposta = sResposta.value.decode("utf-8")

        print(resposta)

    def finalizar_execucao(self):
        self.cbr_lib.NFE_Finalizar()
    
