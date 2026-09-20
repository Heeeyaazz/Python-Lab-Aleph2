"""관리자 전용 API — 회원 목록 조회 / 등급 수정 / 삭제."""
from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def admin_required(fn):
  """등급(role)이 관리자(2)일 때만 통과. 로그인 자체가 안 되어 있으면 401,
  로그인했지만 관리자가 아니면 403(예외 화면 표시용)."""
  @wraps(fn)
  @jwt_required()
  def wrapper(*args, **kwargs):
    user = User.query.get(int(get_jwt_identity()))
    if not user or user.role != User.ROLE_ADMIN:
      return jsonify({'msg': '관리자 권한이 필요합니다.'}), 403
    return fn(*args, **kwargs)
  return wrapper


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
  users = User.query.order_by(User.id).all()
  return jsonify({'users': [
      {'id': u.id, 'username': u.username, 'role': u.role,
       'role_name': User.ROLE_NAMES.get(u.role, '알 수 없음')}
      for u in users
  ]})


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_role(user_id):
  """회원 등급 수정 (관리자 페이지에서 불러온 회원 정보를 수정)."""
  data = request.get_json(silent=True) or {}
  role = data.get('role')
  if role not in (User.ROLE_NORMAL, User.ROLE_GOLD, User.ROLE_ADMIN):
    return jsonify({'msg': 'role 은 0(일반)/1(골드)/2(관리자) 중 하나여야 합니다.'}), 400

  target = User.query.get_or_404(user_id)
  me_id = int(get_jwt_identity())
  if target.id == me_id and role != User.ROLE_ADMIN:
    return jsonify({'msg': '자기 자신의 관리자 권한은 낮출 수 없습니다.'}), 400

  target.role = role
  db.session.commit()
  return jsonify({'msg': '등급이 변경되었습니다.', 'id': target.id, 'role': target.role})


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
  """회원 삭제 (관리자 페이지에서 회원 정보를 불러와서 삭제)."""
  me_id = int(get_jwt_identity())
  if user_id == me_id:
    return jsonify({'msg': '자기 자신은 삭제할 수 없습니다.'}), 400

  target = User.query.get_or_404(user_id)
  try:
    db.session.delete(target)
    db.session.commit()
  except IntegrityError:
    db.session.rollback()
    return jsonify({'msg': '작성한 게시글이 있어 삭제할 수 없습니다. 먼저 게시글을 정리해주세요.'}), 409
  return jsonify({'msg': '삭제되었습니다.'})
