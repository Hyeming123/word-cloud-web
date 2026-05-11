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
        # 데이터 가져오기 (data_get.py 활용)
        title, content = get_best_match_content(query)
        
        if not title or not content:
            return jsonify({'success': False, 'error': '결과를 찾을 수 없습니다.'}), 404

        # 별도의 분석기 없이 텍스트 그대로 워드클라우드 생성
        # (이 방식은 '은/는/이/가' 등의 조사가 그대로 붙어 나옵니다)
        wc = WordCloud(
            background_color='white',
            width=800,
            height=400
        )
        
        wc.generate(content)
        
        # 이미지 변환
        img_buffer = io.BytesIO()
        wc.to_image().save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'title': title,
            'image': img_str
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
