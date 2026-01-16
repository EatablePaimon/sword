import io
from flask import Flask, request, jsonify, send_file
from advancedac import AdvancedAC

app = Flask(__name__)

# 初始化AC
ac = AdvancedAC()
ac.build_from_txt('./wordlib')


@app.route('/check', methods=['POST'])
def quick_check():
    
    data = request.get_json()
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({"error": "参数'text'缺失或非字符串"}), 400
    
    sensitive_found = ac._contains_sensitive(text)
    
    if sensitive_found:
        return jsonify({
            "status": "failed"
        })
    else:
        return jsonify({
            "status": "clean"
        })

@app.route('/scan', methods=['POST'])
def detailed_scan():
    data = request.get_json()
    text = data.get('text', '')
    if not text or not isinstance(text, str):
        return jsonify({"error": "参数'text'缺失或非字符串"}), 400
    
    matches = ac.scan_text(text)
    
    line_breaks = [i for i, c in enumerate(text) if c == '\n']
    line_breaks.append(len(text))
    
    results = []
    for word, start, end, source in matches:  
        # 计算行号
        line_num = next((i+1 for i, pos in enumerate(line_breaks) if pos >= start), 1)
        # 计算行内位置
        prev_break = 0 if line_num == 1 else line_breaks[line_num-2] + 1
        char_start = start - prev_break + 1
        
        results.append({
            "word": word,
            "line": line_num,
            "start_pos": char_start,
            "end_pos": char_start + len(word) - 1,
            "source": source  
        })
    
    if results:
        return jsonify({
            "status": "failed",
            "matches": results
        })
    else:
        return jsonify({
            "status": "clean",
            "matches": results
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)