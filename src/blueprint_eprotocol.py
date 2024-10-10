import MySQLdb
import pytz
from flask import Blueprint, request, jsonify, make_response, abort, current_app
from marshmallow import ValidationError
from typing import Union
from datetime import datetime, date
from extensions import db, auth
from schemas import PreAllocateDocumentsRequestSchema, PreAllocateDocumentsResponseSchema
from datetime import datetime, timezone


eprotocol = Blueprint("eprotocol", __name__)

# def get_departments():
#     cur = db.connection.cursor()
#     cur.execute("SELECT id, des, user_name FROM departments")
#     rv = cur.fetchall()
#     r = dict()
#     for d in rv:
#         r[d.get('id')] = d

#     return r

def str2bool(v: str) -> bool:
    if v is not None:
        return str(v).lower() in ("yes", "true", "t", "1")
    else:
        return False
    
def date2str(v: Union[date, datetime]) -> str:
    if v is None:
        return ""
    
    if isinstance(v, date):
        return v.isoformat()
    else:
        return v.date.isoformat()
    
def datetime2str(v: datetime) -> str:
    if v is None:
        return ""
    
    return v.isoformat()
    
@eprotocol.route("/document/<int:year>/<int:p_id>", methods=["GET"])
def get_document(year, p_id):
    cur = db.connection.cursor()
    
    sql_query = f"SELECT b.id, b.pn, b.io_date, b.summary, b.announce, b.status, b.io_folder, b.io_folder_date, b.i_num, b.io_auth, b.io_auth_date, b.i_place, b.rem, b.completed, b.timestamp, b.mail_id, m.subject, m.mail_address, m.rt, de.des, de.user_name FROM book AS b LEFT JOIN mails AS m ON b.mail_id = m.id LEFT JOIN departments AS de ON de.id = b.modified_by WHERE b.io_year={year} AND b.pn={p_id}"
    #sql_query = f"SELECT * FROM book b WHERE io_year={year} AND pn={p_id}"

    sql_query = f'{sql_query} LIMIT 1'
        
    cur.execute(sql_query)
    rv = cur.fetchone()

    if rv is None:
        # not found !
        return make_response(jsonify({'success': False, 'error': f'document "{p_id}" was not found'}), 404)

    # find associated departments
    cur_2 = db.connection.cursor()
    cur_2.execute(f"SELECT * FROM bookdep bd CROSS JOIN departments d ON bd.department_id=d.id WHERE book_id={rv['id']}")
    rv_2 = cur_2.fetchall()

    our = {
        'id': rv['pn'],
        'date': date2str(rv['io_date']),
        'summary': rv['summary'],
        'cc': rv['announce'],
        'direction': 'out' if rv['status'] == 1 else 'in',
        'folder_archive_id': rv['io_folder'],
        'folder_archive_date': date2str(rv['io_folder_date']),
        'issuing_authority_id': rv['i_num'],
        'issuing_authority': rv['io_auth'],
        'issuing_authority_date': date2str(rv['io_auth_date']),
        'issuing_authority_place': rv['i_place'],
        'comments': rv['rem'],
        'completed': str2bool(rv['completed']),
    }

    if rv['mail_id'] != 0:
        our['incoming_mail'] = {
            'from': rv['mail_address'],
            'subject': rv['subject'],
            'date': rv['rt']
        }

    if rv['timestamp'] is not None:
        our['last_modified'] = {
            'modified_on_date': datetime2str(rv['timestamp']),
            'modified_by_username': rv['user_name'],
            'modified_by_fullname': rv['des'],
        }

    # handle associated deparments
    associated_depart = list()
    for d in rv_2:
       associated_depart.append({
           'fullname': d['des'],
           'username': d['user_name'],
           'assigned_on': datetime2str(d['ch_date']),
           'accept_time': d['accept_time']
       })
    our['associated_departments'] = associated_depart
            
    return make_response(jsonify({'success': True, 'payload': {"document": our}}), 200)


@eprotocol.route("/search", methods=["GET"])
def search_documents():
    cur = db.connection.cursor()
    search_params = {}
    direction_param: str = request.args.get('direction')
    completed_param: str = request.args.get('completed')
    year: str = request.args.get('year')
    summary: str = request.args.get('summary')
    p_id: str = request.args.get('p_id')
    to_from: str = request.args.get('to_from')
    page_number_str: str = request.args.get('page_number', 1)
    page_size_str: str = request.args.get('page_size', 25)

    # normalize page_number and page_size
    try:
        page_number = int(page_number_str)
    except:
        page_number = 1

    try:
        page_size = int(page_size_str)
    except:
        page_size = 25


    if year is not None:
        search_params['io_year'] = year
    
    if p_id is not None:
        search_params['pn'] = f'%{p_id}%'

    if summary is not None:
        search_params['summary'] = f'%{summary}%'

    if direction_param is not None:
        # chekc param
        if direction_param.lower() not in ['in', 'out']:
            return make_response(jsonify({'success': False, 'error': f'specified direction "{direction_param}" not supported'}), 400)
        
        search_params['status'] = 0 if direction_param.lower() == 'in' else 1

    if completed_param is not None:
        completed = str2bool(completed_param)
        search_params['completed'] = 1 if completed else 0

    if to_from is not None:
        search_params['io_auth'] = f'%{to_from}%'

    if len(search_params) == 0:
        return make_response(jsonify({'success': False, 'error': f'missing query params'}), 400)
    
    sql_query = f"SELECT b.pn, b.io_date, b.summary, b.completed, b.status, b.io_auth, b.io_year FROM book b "
    sql_query_for_count = "SELECT COUNT(*) AS count FROM book b "

    # contruct WHERE clause
    sql_where_clause = "WHERE " 
    for k in search_params.keys():
        value = search_params.get(k)
        value_str: str = str(value)
        if "%" in value_str:
            sql_where_clause = sql_where_clause + f'{k} LIKE "{value}" AND '
        else:
            sql_where_clause = sql_where_clause + f'{k}={value} AND '
        
    sql_where_clause = sql_where_clause + "1=1 "

    # construct final queries
    sql_query = sql_query + sql_where_clause + f"ORDER BY pn LIMIT {page_size} OFFSET {(page_number - 1) * page_size}"
    sql_query_for_count = sql_query_for_count + sql_where_clause

    
    cur.execute(sql_query)
    rv = cur.fetchall()

    cur.execute(sql_query_for_count)
    count_r = cur.fetchone().get('count', 0)
    
    documents = list()
    for v in rv:
        item = {
            'id': v['pn'],
            'date': date2str(v['io_date']),
            'summary': v['summary'],
            'direction': 'out' if v['status'] == 1 else 'in',
            'completed': str2bool(v['completed']),
        }
        
        if v['status'] == 1:
            item['to'] = v['io_auth']
        else:
            item['from'] = v['io_auth']

        documents.append(item)

    payload = {
        'total_documents': count_r,
        'page_size': page_size,
        'page_number': page_number,
        'documents': documents
    }


    return make_response(jsonify({'success': True, 'payload': payload}), 200)


@eprotocol.route("/departments", methods=["GET"])
def get_departments():
    cur = db.connection.cursor()
    try:
        name_str: str = request.args.get('name', None)
        page_number_str: str = request.args.get('page_number', 1)
        page_size_str: str = request.args.get('page_size', 25)
        
        # normalize page_number and page_size
        try:
            page_number = int(page_number_str)
        except:
            page_number = 1

        try:
            page_size = int(page_size_str)
        except:
            page_size = 25

        sql_query = "SELECT id, name, des FROM departments "
        sql_query_for_count = "SELECT COUNT(*) AS count FROM departments "
        
        # contruct WHERE clause
        sql_where_clause = "WHERE 1=1 " 
        if name_str is not None:
            sql_where_clause = f"{sql_where_clause} AND name LIKE '%{name_str}%' OR des LIKE '%{name_str}%'" 
        
        # construct final queries
        sql_query = f"{sql_query} {sql_where_clause} ORDER BY name LIMIT {page_size} OFFSET {(page_number - 1) * page_size}"
        sql_query_for_count = f"{sql_query_for_count} {sql_where_clause} "
        
        rv = cur.execute(sql_query)
        rv = cur.fetchall()

        cur.execute(sql_query_for_count)
        count_r = cur.fetchone().get('count', 0)

        departments = list()
        
        for v in rv:
            item = {
                'id': v['id'],
                'name': v['name'],
                'description': v['des'],
            }
            
            departments.append(item)

        payload = {
            'total_departments': count_r,
            'page_size': page_size,
            'page_number': page_number,
            'departments': departments
        }

        return make_response(jsonify({'success': True, 'payload': payload}), 200)
    
    except MySQLdb.Error as e:
        current_app.logger.error(f"mysql error fetching departments: {e}")
        return abort(500, description="error fetching departments")
    finally:
        try:
            cur.close()
        except:
            pass

@eprotocol.route("/document/preallocate", methods=["POST"])
@auth.login_required
def preallocate_documents():

    # Get the JSON data from the request
    json_data = request.get_json()

    if not json_data:
        return abort(400, description="invalid request, json is missing")
    
    request_scheme = PreAllocateDocumentsRequestSchema()

    try:
        # Validate the incoming data using the schema
        data = request_scheme.load(json_data)
    except ValidationError as err:
        # Return validation errors if any
        return abort(400, description={"validation_errors": err.messages})
    
    department_id = data.get('department_id') 
    count = data.get('count')
    issuing_authority = data.get('issuing_authority')
    summary = data.get('summary')
    direction = data.get('direction')
    dry_run = data.get('dry_run')

    now = datetime.now(tz=pytz.timezone('Europe/Athens'))
    year = now.year
    cur = db.connection.cursor()
    
    try:
        cur.execute(f"SELECT max(pn) AS protocol_number FROM book WHERE io_year={year}")
        rv = cur.fetchall()
        current_max_pn = rv[0].get('protocol_number')
        
        # (453771, 10389, '2024-09-19', 2024, NULL, NULL, 'Λ', NULL, NULL, NULL, NULL, 0, 'ΛΥΔΑΚΗ', NULL, 0, NULL, 0, NULL, 0, '2024-09-19 06:23:56', 2);

        book_query = "INSERT INTO book (pn, io_date, io_year, io_auth, status, summary) VALUES (%s, %s, %s, %s, %s, %s)"
        book_rows = list()
        
        for r in range(1, count + 1):
            
            book_rows.append((
                current_max_pn + r,
                now.date().isoformat(),
                year,
                f'{issuing_authority}-{r}',
                0 if direction == 'in' else 1,
                summary
            ))

        # Start transaction
        db.connection.begin()
        
        # Execute many rows in one transaction
        r = cur.executemany(book_query, book_rows)
        
        # fetch inserted IDs
        pn_reserved = [r[0] for r in book_rows]
        q = f'SELECT id, pn FROM book WHERE io_year={year} AND pn IN ({",".join(map(str, pn_reserved))})'
        
        cur.execute(q)
        rv = cur.fetchall()
        
        # associate books with department
        bookdep_query = "INSERT INTO bookdep (book_id, department_id, ch_date) VALUES (%s, %s, %s)"
        bookdep_rows = list()
        book_pns = list()
        for r in rv:
            
            bookdep_rows.append((
                r.get('id'),
                department_id,
                now.strftime('%Y-%m-%d %H:%M:%S')
            ))

            book_pns.append(r.get('pn'))
        
        r = cur.executemany(bookdep_query, bookdep_rows)

        output_data = {
            'department_id': department_id,
            'count': count,
            'issuing_authority': issuing_authority,
            'summary': summary,
            'create_at': now,
            'document_id': book_pns,
            'year': year,
            'direction': direction,
        }

        # Commit the transaction
        if dry_run is False:
            db.connection.commit()
        else:
            db.connection.rollback()

        return PreAllocateDocumentsResponseSchema().dump(output_data)
    except MySQLdb.Error as e:
        current_app.logger.error(f"mysql error: {e}")
        db.connection.rollback()
        
        return abort(500, description="error in database")
    finally:
        try:
            cur.close()
        except:
            pass

    return "errorororor"
    


    