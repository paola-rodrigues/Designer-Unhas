from PyQt6 import uic, QtWidgets
import mysql.connector
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sqlite3
import webbrowser
import requests
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

dados = []
desconto_servico = [False]

# -----------------------------------TELA DE LOGIN ------------------------------------------------------------------


def chama_segunda_tela():
    primeiraTela.label_5.setText('')
    nome_usuario = primeiraTela.lineEdit.text()
    senha = primeiraTela.lineEdit_2.text()

    try:
        banco_dados = sqlite3.connect('banco_usuario.db')
        cursor = banco_dados.cursor()
        cursor.execute("SELECT senha FROM cadastro WHERE login = '{}'".format(nome_usuario))
        senha_banco = cursor.fetchall()
        print(senha_banco[0][0])
        banco_dados.close()

        if senha == senha_banco[0][0]:
            primeiraTela.close()  # Fecha
            cadastroServicosTela.show()  # Abrir
            primeiraTela.lineEdit.setText('')
            primeiraTela.lineEdit_2.setText('')
            primeiraTela.label_5.setText('')
        else:
            primeiraTela.label_5.setText('Dados de login incorretos!')
    except Exception as ex:
        print('Erro: {}'.format(ex))
        primeiraTela.label_5.setText('Dados de login incorretos!')

# --------------------------------------VOLTAR DA TELA DE SERVICO PARA TELA DE CADASTRO--------------------------------


def sair():
    listaServicos.close()
    cadastroServicosTela.show()
# ------------------------------------------ABRIR TELA DE CADASTRO DE USUARIO-----------------------------------------


def abre_tela_cadastro():
    telaCadastro.show()
    primeiraTela.lineEdit.setText('')
    primeiraTela.lineEdit_2.setText('')
    primeiraTela.label_5.setText('')
# ----------------------------------------CADASTRAR USUÁRIO NOVO---------------------------------------------------


def cadastrar():
    nome = telaCadastro.lineEditNome.text().strip().title()
    nome_semEspaco = nome.replace(' ', '')
    login = telaCadastro.lineEditLogin.text().strip()
    cep = telaCadastro.lineEditCep.text().strip()
    senha = telaCadastro.lineEditSenha.text().strip()
    c_senha = telaCadastro.lineEditRepita.text().strip()


# --------------------------------ALGUNS TESTE DE ERRO DO USUARIO--------------------------------------------------

    if not nome_semEspaco.isalpha():
        telaCadastro.labelErroNome.setText('Erro: Deve conter só letras.')
    elif len(nome) < 10:
        telaCadastro.labelErroNome.setText('O nome inválido, digite seu nome completo.')
    else:
        telaCadastro.labelErroNome.setText('')
        if len(login) < 5:
            telaCadastro.labelErroUsuario.setText('Erro: no mínimo 5 caracteres.')
        else:
            telaCadastro.labelErroUsuario.setText('')
            if (len(senha) < 7) or (len(c_senha) < 7):
                telaCadastro.labelSenha.setText('Erro senha: no mínimo 7 caracteres.')
            elif senha != c_senha:
                telaCadastro.labelSenha.setText('Erro: As senhas digitadas estão diferentes.')
            elif senha == login:
                telaCadastro.labelSenha.setText('Erro: A senha deve ser diferente do usuário')
            else:
                telaCadastro.labelSenha.setText('')

# -------------------------------------CADASTRAMENTO NO BANCO DE DADOS SQLITE----------------------------------------

    if ((senha == c_senha) and (len(senha) >= 7) and (len(nome) >= 10) and (len(login) >= 5)
            and (nome_semEspaco.isalpha()) and (senha != login)):
        try:
            banco_usuario = sqlite3.connect('banco_usuario.db')
            cursor = banco_usuario.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS cadastro (nome text,login text,cep text,senha text)')
            cursor.execute("INSERT INTO cadastro VALUES ('" + nome + "','" + login + "','" + cep + "','" + senha + "')")
            banco_usuario.commit()
            banco_usuario.close()
            telaCadastro.lineEditNome.setText('')
            telaCadastro.lineEditLogin.setText('')
            telaCadastro.lineEditSenha.setText('')
            telaCadastro.lineEditRepita.setText('')
            telaCadastro.labelData.setText('')
            telaCadastro.labelHora.setText('')
            telaCadastro.lineEditCep.setText('')
            telaCadastro.labelEndereco.setText('')
            telaCadastro.labelBairro.setText('')
            telaCadastro.labelCidade.setText('')
            telaCadastro.labelUF.setText('')
            telaCadastro.label_7.setText('Usuário cadastrado com sucesso')

        except sqlite3.Error as erro:
            print('Erro ao inserir os dados: ', erro)

# -----------------------------------BANCO DE DADOS MySQL--------------------------------------------------------------


banco = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='cadastro_servicos'
)
# ----------------- LER OS DADOS NA TELA DE SERVICO--------------------------------------------------------------


def servicos_tela():
    try:
        cadastroServicosTela.textoErroLabel.setText('')
        dia = cadastroServicosTela.spinBox.text()
        mesAno = cadastroServicosTela.dateEdit.text()
        cliente = cadastroServicosTela.lineEditCliente.text().strip().title()
        cliente_semEspaco = cliente.replace(' ', '')
        colaborador = cadastroServicosTela.lineEditColaborador.text().strip().title()
        colaborador_semEspaco = colaborador.replace(' ', '')
        desconto = cadastroServicosTela.lineEditDesconto.text().strip()
        valorServico = cadastroServicosTela.lineEditValorServico.text().strip()
        comissao = cadastroServicosTela.lineEditComissao.text().strip()
        formaPagamento = ''

        if cadastroServicosTela.dinheiroButton.isChecked():
            formaPagamento = 'Dinheiro'
        elif cadastroServicosTela.creditoButton.isChecked():
            formaPagamento = 'Crédito'
        elif cadastroServicosTela.debitoButton.isChecked():
            formaPagamento = 'Débito'
        elif cadastroServicosTela.pixButton.isChecked():
            formaPagamento = 'PIX'

        print('cliente:', cliente)
        print('colaborador:', colaborador)
        print('valorServico:', valorServico)
        print('comissao:', comissao)
        print('formaPagamento', formaPagamento)


# --------------------------------ALGUNS TESTE DE ERRO DO USUARIO------------------------------------------------
        if not cliente_semEspaco.isalpha():
            print(cliente_semEspaco.isalpha())
            cadastroServicosTela.erroClienteLabel.setText('Erro: Deve conter só letras.')
        elif len(cliente) < 5:
            cadastroServicosTela.erroClienteLabel.setText('Cliente inválido, no mínimo 5 caracteres.')
        else:
            cadastroServicosTela.erroClienteLabel.setText('')

            if not colaborador_semEspaco.isalpha():
                cadastroServicosTela.ErroColabLabel.setText('Erro: Deve conter só letras.')
            elif len(colaborador) < 5:
                cadastroServicosTela.ErroColabLabel.setText('Colaborador inválido, no mínimo 5 caracteres.')
            else:
                cadastroServicosTela.ErroColabLabel.setText('')

                if not valorServico.isdigit():
                    cadastroServicosTela.ErroServicoLabel.setText('Erro ao inserir os dados.')

                elif int(valorServico) < 20:
                    cadastroServicosTela.ErroServicoLabel.setText('Erro valor inválido.')
                else:
                    cadastroServicosTela.ErroServicoLabel.setText('')

                    if not desconto.isdigit():
                        cadastroServicosTela.ErroDescontoLabel.setText('Erro ao inserir os dados.')

                    elif (int(desconto) / 100) * int(valorServico) > int(valorServico) * 0.1:
                        cadastroServicosTela.ErroDescontoLabel.setText('Erro: máximo de desconto 10,00.')
                    else:
                        cadastroServicosTela.ErroDescontoLabel.setText('')
                        desconto_servico[0] = True

                        if not formaPagamento.isalpha():
                            cadastroServicosTela.textoErroLabel.setText('Erro: Forma de pagamento inválida')
                        else:
                            cadastroServicosTela.textoErroLabel.setText('')

                            if not comissao.isdigit():
                                cadastroServicosTela.ErroComissaoLabel.setText('Erro ao inserir os dados.')

                            elif int(comissao) > 5:
                                cadastroServicosTela.ErroComissaoLabel.setText('Erro: máximo de comissão 5%')
                            else:
                                cadastroServicosTela.ErroComissaoLabel.setText('')

# -------------------------------------CADASTRAMENTO NO BANCO DE DADOS MYSQL------------------------------------

        if (cliente_semEspaco.isalpha() and colaborador_semEspaco.isalpha() and desconto.isdigit()
                and valorServico.isdigit() and comissao.isdigit() and formaPagamento.isalpha() and desconto_servico[0]
                and (len(cliente) >= 5) and (len(colaborador) >= 5) and (int(valorServico) >= 20) and
                (int(comissao) <= 5)):
            cursor = banco.cursor()
            comando_SQL = "INSERT INTO servicos (dia,mesAno,cliente,colaborador,formaPagamento,desconto,valorServico," \
                          "comissao) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) "
            dados = (int(dia), str(mesAno), str(cliente), str(colaborador), str(formaPagamento), float(desconto),
                     float(valorServico), float(comissao))
            cursor.execute(comando_SQL, dados)
            banco.commit()
            cadastroServicosTela.lineEditCliente.setText("")
            cadastroServicosTela.lineEditColaborador.setText("")
            cadastroServicosTela.lineEditDesconto.setText("")
            cadastroServicosTela.lineEditComissao.setText("")
            cadastroServicosTela.lineEditValorServico.setText("")

    except Exception as ex:
        print('Erro: {}'.format(ex))
        telaCadastro.textoErroLabel.setText('Erro ao inserir os dados')

# ---------------- LIMPA  TELA DE SERVICO---------------------------------------------------------------------------


def limpa_tela_servico():
    cadastroServicosTela.lineEditCliente.setText('')
    cadastroServicosTela.lineEditColaborador.setText('')
    cadastroServicosTela.lineEditDesconto.setText('')
    cadastroServicosTela.lineEditComissao.setText('')
    cadastroServicosTela.lineEditValorServico.setText('')
    cadastroServicosTela.textoErroLabel.setText('')

# ---------------- TELA DA LISTA DE SERVIÇOS REALIZADOS-----------------------------------------------------------


def lista_servicos_tela():
    cadastroServicosTela.close()
    listaServicos.show()

    cursor = banco.cursor()
    comando_SQL = 'SELECT * FROM servicos'
    cursor.execute(comando_SQL)
    dados_lidos = cursor.fetchall()

    listaServicos.tableWidget.setRowCount(len(dados_lidos))
    listaServicos.tableWidget.setColumnCount(11)

    for i in range(0, len(dados_lidos)):
        for j in range(0, 11):
            listaServicos.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(dados_lidos[i][j])))

# ---------------- GERADO DE PDF------------------------------------------------------------------------------------


def gerar_pdf():
    try:
        print('gerar pdf')
        cursor = banco.cursor()
        comando_SQL = 'SELECT * FROM servicos'
        cursor.execute(comando_SQL)
        dados_lidos = cursor.fetchall()
        y = 0
        pdf = canvas.Canvas('cadastro_servicos.pdf', pagesize=letter)
        pdf.setFont('Times-Bold', 20)
        pdf.drawString(100, 750, 'Servicos cadastrados:')
        pdf.setFont('Times-Bold', 9)

        pdf.drawString(10, 650, 'ID')
        pdf.drawString(35, 650, 'DIA')
        pdf.drawString(65, 650, 'MÊS/ANO')
        pdf.drawString(120, 650, 'CLIENTE')
        pdf.drawString(190, 650, 'COLAB.')
        pdf.drawString(250, 650, 'FOR.PGTO')
        pdf.drawString(310, 650, 'DESC.(R$)')
        pdf.drawString(370, 650, 'PREÇO(R$)')
        pdf.drawString(430, 650, '%COM.')
        pdf.drawString(480, 650, 'COM.(R$)')
        pdf.drawString(540, 650, 'TOTAL(R$)')

        print('PDF FOI GERADO COM SUCESSO!')

        for i in range(0, len(dados_lidos)):
            y = y + 50
            pdf.drawString(10, 650 - y, str(dados_lidos[i][0]))
            pdf.drawString(35, 650 - y, str(dados_lidos[i][1]))
            pdf.drawString(65, 650 - y, str(dados_lidos[i][2]))
            pdf.drawString(120, 650 - y, str(dados_lidos[i][3]))
            pdf.drawString(190, 650 - y, str(dados_lidos[i][4]))
            pdf.drawString(250, 650 - y, str(dados_lidos[i][5]))
            pdf.drawString(310, 650 - y, str(dados_lidos[i][6]))
            pdf.drawString(370, 650 - y, str(dados_lidos[i][7]))
            pdf.drawString(430, 650 - y, str(dados_lidos[i][8]))
            pdf.drawString(480, 650 - y, str(dados_lidos[i][9]))
            pdf.drawString(540, 650 - y, str(dados_lidos[i][10]))

        pdf.save()
        listaServicos.pdfLabel_2.setText('PDF GERADO')
        print('PDF GERADO')

    except Exception as ex:
        print('Erro: {}'.format(ex))
        listaServicos.pdfLabel_2.setText('Erro')
# ---------------- LINK DO WHATSAPP---------------------------------------------------


def link_whatsapp():
    # utilização da biblioteca webbrowser abrir o link
    webbrowser.open('https://wa.me/qr/WN36ZNF2RBDFM1')
# ---------------- LINK DO INSTAGRAM---------------------------------------------------


def link_instagram():
    webbrowser.open('https://www.instagram.com/angelica_vieira_rodrigues/')


# ---------------- EXCLUIR DADOS DA LISTA--------------------------------------------------

def excluir():
    linha_dados = listaServicos.tableWidget.currentRow()
    listaServicos.tableWidget.removeRow(linha_dados)

    cursor = banco.cursor()
    cursor.execute('SELECT id FROM servicos')
    dados_lidos = cursor.fetchall()
    id_valor = dados_lidos[linha_dados][0]
    cursor.execute('DELETE FROM servicos WHERE id={}'.format(str(id_valor)))

# -------------------------------BUSCAR CEP-------------------------------------------------------------


def buscar_cep():

    try:
        cep = telaCadastro.lineEditCep.text().strip()
        response = requests.get('https://viacep.com.br/ws/{}/json/'.format(cep))

        print(response.status_code)
        print(response.text)
        dados_cep = response.json()
        print(dados_cep['logradouro'])
        print(type(dados_cep))
        dados.append(dados_cep['logradouro'])
        dados.append(dados_cep['bairro'])
        dados.append(dados_cep['localidade'])
        dados.append(dados_cep['uf'])
        print(dados)

        data_atual = datetime.now()
        hora = data_atual.strftime('%H:%M:%S')
        data = data_atual.strftime('%d/%m/%Y')
        telaCadastro.labelData.setText(data)
        telaCadastro.labelHora.setText(hora)
        if dados != '':
            telaCadastro.label_7.setText('')
            telaCadastro.labelEndereco.setText(dados[0])
            telaCadastro.labelBairro.setText(dados[1])
            telaCadastro.labelCidade.setText(dados[2])
            telaCadastro.labelUF.setText(dados[3])

    except Exception as ex:
        print('Erro: {}'.format(ex))
        telaCadastro.label_7.setText('O CEP digitado está incorreto')
        
# ---------------------------------------------------------------------------------------------


def email_tela():
    EmailTela.show()
    listaServicos.close()


def enviar_email():
    try:
        nome = EmailTela.lineEditNome.text().strip().title()
        email_destino = EmailTela.lineEditEmail.text().strip()

        corpo_email = f"""   
        Olá {nome},
        Como você está?
        Espero que você e seus familiares estejam bem <3.

        Segue relatório de serviço.        

        Atenciosamente,
        Paola do Nascimento
        paola.n.rodrigues@gmail.com   
        """

        msg = MIMEMultipart()  # Crie uma mensagem multiplas parte
        msg['Subject'] = "Meu Lindo Relatório de Serviço - Projeto IP"  # Email do Assunto
        msg['From'] = 'paola.rodrigues.ads@gmail.com'  # Email do remetente
        msg['To'] = email_destino  # Email do destinatário
        password = '#nota10@ads'  # Senha do email do remetente

        # Adicionar ao corpo do email e através função attach() juntando as informações do e-mail
        msg.attach(MIMEText(corpo_email, "plain"))

        # Declaramos o nome do arquivo e o caminho
        arquivo = 'cadastro_servicos.pdf'

        # rb  - 'r+' abre para leitura e gravação, 'b'  abre no modo binário
        attachment = open(arquivo, 'rb')

        part = MIMEBase('application', 'octet-stream')
        # Destinatario pode baixar o arquivo automaticamente
        part.set_payload(attachment.read())
        # Codifique o arquivo em caracteres ASCII para enviar por e-mail
        encoders.encode_base64(part)
        # Adicionar cabeçalho como par chave / valor à parte do anexo
        part.add_header('Content-Disposition', "attachment; filename= %s" % arquivo)

        # Adicionar anexo à mensagem e converter mensagem em string
        msg.attach(part)
        # attachment.close()
        text = msg.as_string()

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        # Faça login no servidor
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], text)
        s.quit()
        print('Email enviado')
        msgEmail.show()
        msgEmail.labelMsg.setText("Email enviado!")

    except Exception as ex:
        print('erro desconhecido. erro: {}'.format(ex))
        msgEmail.show()
        msgEmail.labelMsg.setText("Email incorreto!")


def fechar_msg():
    msgEmail.close()


def sair_msg_email():
    msgEmail.close()
    EmailTela.close()
# ---------------------------------------------------------------------------------------------


app = QtWidgets.QApplication([])
cadastroServicosTela = uic.loadUi('cadastroServicosTela.ui')
listaServicos = uic.loadUi('listaServicos.ui')
primeiraTela = uic.loadUi('primeiraTela.ui')
telaCadastro = uic.loadUi('telaCadastro.ui')
EmailTela = uic.loadUi("telaEmail.ui")
msgEmail = uic.loadUi("msgEmail.ui")
# ------Button Primeira Tela ---------------------------------
primeiraTela.pushButton.clicked.connect(chama_segunda_tela)
primeiraTela.pushButton_2.clicked.connect(abre_tela_cadastro)
primeiraTela.whatsappButton.clicked.connect(link_whatsapp)
primeiraTela.instagramButton.clicked.connect(link_instagram)
# ------Button Tela de Cadastro-------------------------------
telaCadastro.pushButton.clicked.connect(cadastrar)
telaCadastro.pushButton_2.clicked.connect(buscar_cep)
# ------Button Cadastro de Servico --------------------------
cadastroServicosTela.pushButton.clicked.connect(servicos_tela)
cadastroServicosTela.pushButton_2.clicked.connect(limpa_tela_servico)
cadastroServicosTela.pushButton_3.clicked.connect(lista_servicos_tela)
# ------Button Lista Servicos -----------------------------
listaServicos.pdfButton.clicked.connect(gerar_pdf)
listaServicos.voltarButton.clicked.connect(sair)
listaServicos.excluirButton.clicked.connect(excluir)
listaServicos.MsmServicoButton.clicked.connect(email_tela)

msgEmail.FecharMsgButton.clicked.connect(fechar_msg)
msgEmail.sairMsgButton.clicked.connect(sair_msg_email)
EmailTela.pushButton.clicked.connect(enviar_email)

# Abrir Tela inicial
primeiraTela.show()
app.exec()
