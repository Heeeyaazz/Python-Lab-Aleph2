from extensions import db


class User(db.Model):
  __tablename__ = 'users'

  # 등급(권한) 상수 — 숫자가 클수록 상위 권한
  ROLE_NORMAL = 0   # 일반 등급 (최초 가입)
  ROLE_GOLD = 1     # 골드 등급 (중간 관리자)
  ROLE_ADMIN = 2    # 관리자

  ROLE_NAMES = {ROLE_NORMAL: '일반 등급', ROLE_GOLD: '골드 등급', ROLE_ADMIN: '관리자'}

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(255), nullable=False)   # 해시만 저장(평문 금지)
  role = db.Column(db.Integer, nullable=False, default=ROLE_NORMAL)

  def __repr__(self):
    return f'<User {self.username} role={self.role}>'