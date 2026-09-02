from datetime import datetime
import json
from flask import Flask, Response, render_template_string
import pymysql
import requests

app = Flask(__name__)

# DB 연결 설정 (root / 123456)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def get_db_connection(use_db=True):
    """안전한 DB 연결 생성을 위한 헬퍼 함수"""
    config = DB_CONFIG.copy()
    if use_db:
        config["database"] = "github_db"
    return pymysql.connect(**config)


def init_db():
    """데이터베이스 및 테이블 자동 생성"""
    # 초기 생성 시에는 database 지정을 제외하고 연결
    with get_db_connection(use_db=False) as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS github_db;")
            cursor.execute("USE github_db;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    current_user_url VARCHAR(255),
                    authorizations_url VARCHAR(255),
                    code_search_url VARCHAR(255),
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()


@app.route("/")
def index():
    init_db()

    # 1. GitHub API 호출 및 데이터 수집
    r = requests.get("https://api.github.com")
    data = r.json()

    # 2. MySQL에 데이터 저장
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO api_responses (current_user_url, authorizations_url, code_search_url)
                VALUES (%s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    data.get("current_user_url"),
                    data.get("authorizations_url"),
                    data.get("code_search_url"),
                ),
            )
        conn.commit()

    return "데이터가 성공적으로 수집 및 저장되었습니다! <br><a href='/view'>웹으로 보기</a> | <a href='/download'>파일로 다운로드</a>"


@app.route("/view")
def view_data():
    """저장된 내용을 간단한 웹 화면으로 출력"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM api_responses ORDER BY id DESC")
            rows = cursor.fetchall()

    html = """
    <h2>GitHub API 응답 데이터 목록</h2>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>ID</th>
            <th>Current User URL</th>
            <th>Authorizations URL</th>
            <th>Code Search URL</th>
            <th>Fetched At</th>
        </tr>
        {% for row in rows %}
        <tr>
            <td>{{ row.id }}</td>
            <td>{{ row.current_user_url }}</td>
            <td>{{ row.authorizations_url }}</td>
            <td>{{ row.code_search_url }}</td>
            <td>{{ row.fetched_at }}</td>
        </tr>
        {% endfor %}
    </table>
    <br><a href="/">데이터 새로 수집하기</a>
    """
    return render_template_string(html, rows=rows)


@app.route("/download")
def download_file():
    """저장된 내용을 파일 형식(JSON)으로 출력 및 다운로드"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM api_responses")
            rows = cursor.fetchall()

    # datetime 객체 JSON 직렬화 오류 방지 변환
    for row in rows:
        if "fetched_at" in row and isinstance(row["fetched_at"], datetime):
            row["fetched_at"] = row["fetched_at"].strftime("%Y-%m-%d %H:%M:%S")

    json_data = json.dumps(rows, ensure_ascii=False, indent=4)

    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=github_data.json"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)