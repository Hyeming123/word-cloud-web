from flask import Flask, render_template, request, jsonify
from data_get import get_best_match_content
from wordcloud import WordCloud
from konlpy.tag import Okt  # 추가: 한글 형태소 분석기
import io
import base64
import os
import re

app = Flask(__name__)

# 1. 커스텀 불용어 리스트 정의
# 위키백과 등에서 자주 나오지만 의미 없는 단어들을 추가하세요.
CUSTOM_STOPWORDS = {
    '있는', '대한', '있으며', '위해', '통해', '하며', '관련', '내용', 
    '때문', '경우', '의해', '그대로', '또한', '하지만', '그리고',
    '이름', '가지', '여러', '일부', '대해', '가장', '단어', '문장'
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
        # 한글/영문만 남기고 특수문자 제거
        clean_content = re.sub(r'[^가-힣a-zA-Z\s]', '', content)
        
        okt = Okt()
        # 명사만 추출하고, 길이가 2글자 이상이며 불용어 리스트에 없는 것만 필터링
        nouns = [word for word in okt.nouns(clean_content) 
                 if len(word) > 1 and word not in CUSTOM_STOPWORDS]
        
        # 워드클라우드에 넣을 수 있도록 다시 공백으로 합침
        final_text = ' '.join(nouns)

        # 3. 워드클라우드 설정
        font_path = 'NanumGothic.ttf'
        if not os.path.exists(font_path):
            font_path = r'C:\Windows\Fonts\malgun.ttf'
            if not os.path.exists(font_path):
                font_path = None

        wc = WordCloud(
            font_path=font_path,
            background_color='white',
            width=800,
            height=400,
            max_words=100, # 핵심 단어 위주로 보이게 숫자를 조금 줄였습니다.
            colormap='viridis'
        )

        # 4. 이미지 생성
        if not final_text.strip(): # 필터링 후 내용이 없는 경우 대비
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
        print(f"Error generating word cloud: {e}")
        return jsonify({'success': False, 'error': '서버 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
