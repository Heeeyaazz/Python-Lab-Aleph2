"""화면(HTML) 라우트만 모음. 데이터는 각 페이지의 JS 가 API 로 가져온다."""
from flask import Blueprint, render_template

page_bp = Blueprint('page', __name__)


@page_bp.route('/')
def index():
  return render_template('index.html')


@page_bp.route('/dashboard')
def dashboard():
  """보안 이벤트 대시보드 (n8n 이 저장한 허용/거부 기록)."""
  return render_template('dashboard.html')


@page_bp.route('/public-posts')
def public_posts_page():
  return render_template('public_posts.html')


@page_bp.route('/public-posts/<int:uc_seq>')
def public_post_detail_page(uc_seq):
  return render_template('public_detail.html', uc_seq=uc_seq)


@page_bp.route('/gold')
def gold_page():
  """골드 등급(1) 이상 전용 화면. 실제 접근 통제는 /api/gold/info 호출 결과로
  클라이언트가 판단해 예외 화면을 그린다(토큰이 localStorage 에 있어 서버 페이지
  라우트 단계에서는 검사하지 않는 구조 — 다른 페이지들과 동일한 방식)."""
  return render_template('gold.html')


@page_bp.route('/admin')
def admin_page():
  """관리자(2) 전용 화면. 실제 접근 통제는 /api/admin/users 호출 결과로 판단."""
  return render_template('admin.html')