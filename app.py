from flask import Flask, render_template, request, jsonify
from data_get import get_best_match_content
from wordcloud import WordCloud
from kiwipiepy import Kiwi # Kiwi 사용
import io
import base64
import os
import re

# Kiwi 초기화 (전역 설정)
kiwi = Kiwi()
app = Flask(__name__)

# 1. 커스텀 불용어 리스트
CUSTOM_STOPWORDS = {
    '있는', '대한', '있으며', '위해', '통해', '하며', '관련', '내용', 
    '때문', '경우', '의해', '그대로', '또한', '하지만', '그리고',
    '이름', '가지', '여러', '일부', '대해', '가장', '단어', '문장', '위키백과'
}

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
            return jsonify({'success': False, 'error': f"'{query}'에 대한 검색 결과가 없습니다."}), 404

        # 2. 텍스트 정제 및 명사 추출
        clean_content = re.sub(r'[^가-힣a-zA-Z\s]', ' ', content) # 특수문자를 공백으로 치환
        
        # Kiwi를 이용한 형태소 분석
        # tokenize: 텍스트를 형태소 단위로 분리
        tokens = kiwi.tokenize(clean_content)
        
        # 명사(NNG, NNP)만 추출 + 2글자 이상 + 불용어 제외
        nouns = [
            t.form for t in tokens 
            if t.tag in ('NNG', 'NNP') and len(t.form) > 1 and t.form not in CUSTOM_STOPWORDS
        ]
        
        final_text = ' '.join(nouns)

        # 3. 워드클라우드 설정 (Render 환경 고려)
        # 프로젝트 루트에 NanumGothic.ttf가 있다고 가정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, 'NanumGothic.ttf')
        
        if not os.path.exists(font_path):
            # 로컬 윈도우 환경용 백업
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

        # 4. 이미지 생성
        if not final_text.strip():
            return jsonify({'success': False, 'error': '추출된 유효한 단어가 없습니다.'}), 400
            
        wc.generate(final_text)
        
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
        # 구체적인 에러 로그를 서버 터미널에 출력
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'서버 오류: {str(e)}'}), 500

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
