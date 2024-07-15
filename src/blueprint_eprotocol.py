from flask import Blueprint, request, Response, jsonify, make_response
from typing import Union
from datetime import datetime, date
from extensions import db
from collections import OrderedDict
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
    
    direction_param: str = request.args.get('direction')
    if direction_param is not None:
        # chekc param
        if direction_param.lower() not in ['incoming', 'outgoing']:
            return make_response(jsonify({'success': False, 'error': f'specified direction "{direction_param}" not supported'}), 400)
        
        direction = direction_param.lower()

    else:
        direction = None

    sql_query = f"SELECT b.id, b.pn, b.io_date, b.summary, b.announce, b.status, b.io_folder, b.io_folder_date, b.i_num, b.io_auth, b.io_auth_date, b.i_place, b.rem, b.completed, b.timestamp, b.mail_id, m.subject, m.mail_address, m.rt, de.des, de.user_name FROM book AS b LEFT JOIN mails AS m ON b.mail_id = m.id LEFT JOIN departments AS de ON de.id = b.modified_by WHERE b.io_year={year} AND b.pn={p_id}"
    #sql_query = f"SELECT * FROM book b WHERE io_year={year} AND pn={p_id}"


    if direction:
        sql_query = f'{sql_query} AND status={1 if direction == "outgoing" else 0}'

    sql_query = f'{sql_query} LIMIT 1'
        
    cur.execute(sql_query)
    rv = cur.fetchone()

    if rv is None:
        # not found !
        return make_response(jsonify({'success': False, 'error': f'document "{p_id}" was not found'}), 404)

    print(rv)
    print(type(rv))
    print(type(rv['io_auth_date']))
    
    # find associated departments
    cur_2 = db.connection.cursor()
    cur_2.execute(f"SELECT * FROM bookdep bd CROSS JOIN departments d ON bd.department_id=d.id WHERE book_id={rv['id']}")
    rv_2 = cur_2.fetchall()
    print(rv_2)

    our = {
        'id': rv['pn'],
        'date': date2str(rv['io_date']),
        'summary': rv['summary'],
        'cc': rv['announce'],
        'direction': 'outgoing' if rv['status'] == 1 else 'incoming',
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
         
    r = OrderedDict([
        ('our', our),
        ('o', rv)
    ])
       
    return make_response(jsonify({'success': True, 'document': our}), 200)
    #return jsonify(r)
    