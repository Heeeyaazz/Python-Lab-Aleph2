"""회원가입 / 로그인 / 내 정보 조회."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
  data = request.get_json(silent=True) or {}
  if not data.get('username') or not data.get('password'):
    return jsonify({'msg': 'username, password 는 필수입니다.'}), 400
  if User.query.filter_by(username=data['username']).first():
    return jsonify({'msg': '이미 존재하는 사용자입니다.'}), 400

  # 회원가입 시 등급은 항상 '일반 등급' 으로 시작한다.
  # 단, 테스트 편의를 위해 시스템에 계정이 하나도 없는 최초 1회에 한해
  # 첫 가입자를 관리자로 부트스트랩한다(그래야 관리자 페이지에 아무도 못 들어가는
  # 상황을 피할 수 있다). 이후 가입자는 모두 일반 등급.
  is_first_user = User.query.count() == 0
  user = User(username=data['username'],
              password=generate_password_hash(data['password']),
              role=User.ROLE_ADMIN if is_first_user else User.ROLE_NORMAL)
  db.session.add(user)
  db.session.commit()

  msg = '회원가입 성공'
  if is_first_user:
    msg += ' (최초 가입자이므로 관리자 권한이 부여되었습니다)'
  return jsonify({'msg': msg, 'role': user.role}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
  data = request.get_json(silent=True) or {}
  user = User.query.filter_by(username=data.get('username')).first()
  if not user or not check_password_hash(user.password, data.get('password', '')):
    return jsonify({'msg': '아이디 또는 비밀번호가 잘못되었습니다.'}), 401

  token = create_access_token(identity=str(user.id))
  return jsonify(access_token=token, username=user.username, role=user.role)


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
  """헤더에 로그인 유저명 + 등급을 표시하기 위한 내 정보 조회."""
  user = User.query.get(int(get_jwt_identity()))
  if not user:
    return jsonify({'msg': '사용자를 찾을 수 없습니다.'}), 404
  return jsonify({
      'id': user.id,
      'username': user.username,
      'role': user.role,
      'role_name': User.ROLE_NAMES.get(user.role, '알 수 없음'),
  })