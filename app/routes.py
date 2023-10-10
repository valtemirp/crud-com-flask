from app import app
from flask import render_template, request, redirect, url_for, flash, get_flashed_messages, session
import pyodbc
from datetime import datetime
from app import log


@app.route('/', methods=['GET','POST'])
def mostrar():
    # Salvando session de usuario em txt(bonus)
    log_message = log.collect_request_data()
    log.log_request_data(log_message)

    # Estabelecendo conexão com o banco de dados usando ODBC
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=;'
                            'DATABASE=sistema_biblioteca;'
                            'UID=;'
                            'PWD=')

    cursor = connection.cursor()
    
    # Executando uma consulta simples para demonstração
    cursor.execute('SELECT TOP 10 * FROM livro')
    rows = cursor.fetchall()


    # Fechando a conexão
    cursor.close()
    connection.close()
    # Renderizando o template e passando os dados dos livros
    return render_template('index.html', books=rows)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        # Estabelecendo conexão
        connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=;'
                            'DATABASE=sistema_biblioteca;'
                            'UID=;'
                            'PWD=')
        cursor = connection.cursor()

        # Pegando dados do formulário
        titulo = request.form.get('titulo')
        ano = request.form.get('ano')
        autor = request.form.get('autor')

        # Inserindo no banco (removendo numero_registro da inserção)
        cursor.execute('INSERT INTO livro (titulo, ano_publicacao, autor) VALUES (?,?,?)', titulo, ano, autor)
        flash('Livro adicionado com sucesso!', 'success')
        # Commit e fechando conexão
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('mostrar'))
    else:
        return render_template('cadastrar.html')


@app.route('/editar', methods=['POST', 'GET'])
def editar():
    print("Ação recebida:", request.form.get('action_type'))

    if request.method == 'POST':
        action_type = request.form.get('action_type')
        
        if action_type == "edit":
            # Define o ID do livro como "em edição" na session
            session['editing_id'] = request.form.get('id')
        
        elif action_type == "save" and 'editing_id' in session:
            # Pega o ID do livro em edição da session
            editing_id = session['editing_id']

            # Atualizar o livro no banco de dados
            titulo = request.form.get('titulo')
            ano = request.form.get('ano')
            autor = request.form.get('autor')

            # Conecte-se ao banco de dados e atualize o registro
            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=;'
                            'DATABASE=sistema_biblioteca;'
                            'UID=;'
                            'PWD=')
            cursor = connection.cursor()

            # Use parâmetros nomeados para evitar problemas de injeção SQL
            cursor.execute('UPDATE livro SET titulo = ?, ano_publicacao = ?, autor = ? WHERE numero_registro = ?', (titulo, ano, autor, editing_id))

            connection.commit()
            cursor.close()
            connection.close()

            # Remove o ID do livro em edição da session
            session.pop('editing_id', None)
        return redirect(url_for('mostrar'))
    else:
        return redirect(url_for('mostrar'))



@app.route('/excluir/<int:id>', methods=['GET'])
def excluir(id):
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            ';'
                            'DATABASE=sistema_biblioteca;'
                            'UID=;'
                            'PWD=')
    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM livro WHERE numero_registro = ?', id)
    flash('Livro excluído com sucesso!', 'danger')
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('mostrar'))
