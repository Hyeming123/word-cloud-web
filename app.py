from flask import Flask, render_template, request, jsonify
from data_get import get_best_match_content
from wordcloud import WordCloud
import io
import base64
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': '검색어를 입력해 주세요.'}), 400

    try:
        title, content = get_best_match_content(query)
        
        if not title or not content:
            return jsonify({'success': False, 'error': '결과를 찾을 수 없습니다.'}), 404

        # --- 폰트 설정 추가 구간 ---
        # 1. 프로젝트 폴더에 있는 나눔고딕 확인
        font_path = 'NanumGothic.ttf' 
        
        # 2. 파일이 없으면 시스템 기본 폰트 시도 (서버 환경 대응)
        if not os.path.exists(font_path):
            # 로컬 윈도우 개발 환경용 경로
            font_path = r'C:\Windows\Fonts\malgun.ttf'
            if not os.path.exists(font_path):
                # 최후의 수단: 폰트 경로를 지정하지 않음 (이 경우 한글이 깨질 수 있음)
                font_path = None
        # ------------------------

        wc = WordCloud(
            font_path=font_path,     # 설정한 폰트 경로 적용
            background_color='white',
            width=800,
            height=400
        )
        
        wc.generate(content)
        
        img_buffer = io.BytesIO()
        wc.to_image().save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'title': title,
            'image': img_str,
            'url': f"https://ko.wikipedia.org/wiki/{title.replace(' ', '_')}"
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
