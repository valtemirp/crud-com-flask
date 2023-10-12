from app import app
from flask import render_template, request, redirect, url_for, flash, get_flashed_messages, session, request
import pyodbc
from datetime import datetime
from app import log


@app.route('/')
def mostrar():
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=VALTEMIR;DATABASE=sistema_biblioteca;Trusted_Connection=yes')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM livro')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    # Calcule o número total de páginas com base na quantidade de livros e itens por página
    total_books = len(rows)
    items_per_page = 10
    total_pages = (total_books + items_per_page - 1) // items_per_page

    return render_template('index.html', books=rows, total_pages=total_pages)


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        # Estabelecendo conexão
        connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=VALTEMIR;DATABASE=sistema_biblioteca;Trusted_Connection=yes')

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
            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=VALTEMIR;DATABASE=sistema_biblioteca;Trusted_Connection=yes')

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
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=VALTEMIR;DATABASE=sistema_biblioteca;Trusted_Connection=yes')

    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM livro WHERE numero_registro = ?', id)
    flash('Livro excluído com sucesso!', 'danger')
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('mostrar'))

@app.route('/buscar_livros', methods=['POST'])
def buscar_livros():
    livro = request.form.get('livro')

    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=VALTEMIR;DATABASE=sistema_biblioteca;Trusted_Connection=yes')
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

@app.route('/lista_livros', methods=['GET'])
def lista_livros():
    # Obtenha o número da página da consulta de URL
    page = int(request.args.get('page', 1))

    # Defina o número de itens por página
    items_per_page = 10

    # Consulta o banco de dados para obter a lista de livros
    connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=VALTEMIR;DATABASE=sistema_biblioteca;Trusted_Connection=yes')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM livro')
    all_books = cursor.fetchall()

    # Calcule o índice de início e fim com base na página atual
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Calcule a lista de livros para a página atual
    books = all_books[start_idx:end_idx]

    # Calcule o número total de páginas
    total_pages = (len(all_books) + items_per_page - 1) // items_per_page

    # Calcule se há uma página anterior e/ou próxima
    has_prev_page = page > 1
    has_next_page = page < total_pages

    # Calcule as páginas anterior e próxima
    prev_page = page - 1 if has_prev_page else None
    next_page = page + 1 if has_next_page else None

    cursor.close()
    connection.close()

    return render_template('index.html', books=books, page=page, total_pages=total_pages, prev_page=prev_page, next_page=next_page, has_next_page=has_next_page)

