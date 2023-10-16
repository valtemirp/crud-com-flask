from app import app
from flask import render_template, request, redirect, url_for, flash, get_flashed_messages, session, request, Response, render_template_string
import pyodbc,  bleach
from datetime import datetime
from app import log
import brazilcep


@app.after_request
def add_ngrok_header(response):
    response.headers["ngrok-skip-browser-warning"] = "1"
    return response

@app.route('/')
def mostrar():
    # Salvando session de usuario em txt(bonus)
    log_message = log.collect_request_data()
    log.log_request_data(log_message)
    response = Response("Hello, World!")
    response.headers["ngrok-skip-browser-warning"] = "1"
    editing_id = request.args.get('editing_id')
    
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=02LAB108PC01\SQLDEVELOPER;'
                            'DATABASE=sistema_biblioteca;'
                            'UID=sa;'
                            'PWD=sa')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM livro')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Encontre o livro que está sendo editado, se houver algum
    editing_book = next((book for book in rows if str(book[3]) == editing_id), None)

    # Calcule o número total de páginas com base na quantidade de livros e itens por página
    total_books = len(rows)
    items_per_page = 10
    total_pages = (total_books + items_per_page - 1) // items_per_page

    return render_template('index.html', books=rows, total_pages=total_pages, editing_book=editing_book)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        MAX_LENGTH = 255  # ou qualquer outro valor que você desejar

        # Pegando dados do formulário e sanitizando
        titulo = bleach.clean(request.form.get('titulo'))
        ano = bleach.clean(request.form.get('ano'))
        autor = bleach.clean(request.form.get('autor'))

        if len(titulo) > MAX_LENGTH or len(autor) > MAX_LENGTH:
            flash('Os campos não podem exceder 255 caracteres!', 'danger')
            return render_template('cadastrar.html')

        if not (len(ano) == 4 and ano.isdigit()):
            flash('O ano deve conter exatamente 4 dígitos!', 'danger')
            return render_template('cadastrar.html')

        # Estabelecendo conexão
        connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=02LAB108PC01\SQLDEVELOPER;'
                            'DATABASE=sistema_biblioteca;'
                            'UID=sa;'
                            'PWD=sa')

        cursor = connection.cursor()

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

            flash("Livro editado com sucesso!", "success")

            # Conecte-se ao banco de dados e atualize o registro
            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=02LAB108PC01\SQLDEVELOPER;'
                            'DATABASE=sistema_biblioteca;'
                            'UID=sa;'
                            'PWD=sa')

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

@app.route('/excluir', methods=['POST'])
def excluir():
    action_type = request.form.get('action_type')
    
    if action_type == "delete":
        # Obtenha o ID do livro a ser excluído do formulário
        id = request.form.get('id')

        if id is not None:
            try:
                id = int(id)
            except ValueError:
                flash('ID inválido para exclusão.', 'danger')
                return redirect(url_for('mostrar'))

            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=02LAB108PC01\SQLDEVELOPER;'
                            'DATABASE=sistema_biblioteca;'
                            'UID=sa;'
                            'PWD=sa')
            cursor = connection.cursor()

            cursor.execute('DELETE FROM livro WHERE numero_registro = ?', id)
            connection.commit()
            cursor.close()
            connection.close()

            flash('Livro excluído com sucesso!', "success")
        else:
            flash('ID de livro não fornecido para exclusão.', "danger")

    return redirect(url_for('mostrar'))


@app.route('/buscar_livros', methods=['POST'])
def buscar_livros():
    livro = request.form.get('livro')

    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=02LAB108PC01\SQLDEVELOPER;'
                            'DATABASE=sistema_biblioteca;'
                            'UID=sa;'
                            'PWD=sa')
    cursor = connection.cursor()

    if livro:
        cursor.execute('SELECT * FROM livro WHERE titulo = ?', (livro,))
    else:
        cursor.execute('SELECT * FROM livro')

    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Cálculo do número total de páginas
    total_books = len(rows)
    items_per_page = 10
    total_pages = (total_books + items_per_page - 1) // items_per_page

    return render_template('index.html', books=rows, total_pages=total_pages)

@app.route('/cep', methods=['GET', 'POST'])
def cep():
    cep_info = brazilcep.get_address_from_cep('37503-130')

    # Construir a lista de informações do CEP dinamicamente
    info_list = ""
    for key, value in cep_info.items():
        info_list += f"<li><strong>{key.capitalize()}:</strong> {value}</li>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Informações do CEP</title>
    </head>
    <body>
        <h1>Informações do CEP: {cep_info.get('cep', 'N/A')}</h1>
        <ul>
            {info_list}
        </ul>
    </body>
    </html>
    """

    return html_content


@app.route('/pagamento', methods=['GET', 'POST'])
def pagamento():
    metodo_pagamento = None
    if request.method == 'POST':
        metodo_pagamento = request.form['metodo_pagamento']
    return render_template('pagamento.html', metodo_pagamento=metodo_pagamento)

