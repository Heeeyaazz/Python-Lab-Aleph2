"""골드 등급 전용 API — 등급(role) 1 이상(골드, 관리자)만 접근 가능."""
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import User

gold_bp = Blueprint('gold', __name__, url_prefix='/api/gold')


@gold_bp.route('/info', methods=['GET'])
@jwt_required()
def gold_info():
  user = User.query.get(int(get_jwt_identity()))
  if not user:
    return jsonify({'msg': '사용자를 찾을 수 없습니다.'}), 404
  if user.role < User.ROLE_GOLD:
    return jsonify({'msg': '골드 등급 이상만 접근할 수 있습니다.'}), 403

  return jsonify({
      'msg': '골드 등급 전용 콘텐츠입니다. 중간 관리자에게만 보이는 정보입니다.',
      'username': user.username,
      'role': user.role,
      'role_name': User.ROLE_NAMES.get(user.role, '알 수 없음'),
  })
