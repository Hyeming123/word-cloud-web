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
            return jsonify({'success': False, 'error': f"'{query}'에 대한 위키백과 검색 결과가 없습니다."}), 404

        # 워드클라우드 생성 설정
        # 한글 폰트 경로 설정 (배포 환경을 고려하여 로컬 폰트 우선 사용)
        font_path = 'NanumGothic.ttf'
        if not os.path.exists(font_path):
            # 로컬에 없으면 시스템 경로 확인 (Windows)
            font_path = r'C:\Windows\Fonts\malgun.ttf'
            if not os.path.exists(font_path):
                font_path = None

        wc = WordCloud(
            font_path=font_path,
            background_color='white',
            width=800,
            height=400,
            max_words=150,
            colormap='viridis'
        )

        # 워드클라우드 이미지 생성
        wc.generate(content)
        
        # 이미지를 바이트로 변환 후 base64 인코딩
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
        print(f"Error generating word cloud: {e}")
        return jsonify({'success': False, 'error': '서버 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    # 템플릿 폴더가 없으면 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Render 배포를 위해 환경 변수에서 포트를 가져오고 0.0.0.0으로 바인딩
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)여기에 추가해줘
