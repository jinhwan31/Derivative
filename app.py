from flask import Flask, render_template, request
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image as PILImage
import base64

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    derivative_expr = ''
    derivative_value = ''
    graph_url = ''
    
    if request.method == "POST":
        expr_str = request.form["function"]
        x_val_str = request.form["x_value"]
        
        try:
            # sympy로 함수와 도함수 계산
            x = sp.symbols('x')
            expr = sp.sympify(expr_str)
            derivative_expr = sp.diff(expr, x)
            f_prime = sp.lambdify(x, derivative_expr, "numpy")

            # x 값 입력 처리
            if x_val_str:
                x_val = float(x_val_str)
                derivative_value = f_prime(x_val)
            else:
                derivative_value = "x 값을 입력하세요."

            # 그래프 생성
            graph_url = generate_graph(expr, derivative_expr)
        
        except Exception as e:
            derivative_expr = "오류가 발생했습니다. 입력을 확인하세요."
            derivative_value = str(e)

    return render_template("index.html", 
                           derivative_expr=derivative_expr,
                           derivative_value=derivative_value,
                           graph_url=graph_url)

def generate_graph(expr, derivative_expr):
    # x 값 범위 설정
    x_vals = np.linspace(-10, 10, 400)
    
    # 함수와 도함수 계산
    f = sp.lambdify('x', expr, "numpy")
    f_prime = sp.lambdify('x', derivative_expr, "numpy")

    y_vals = f(x_vals)
    dy_vals = f_prime(x_vals)

    # 그래프 그리기
    plt.figure(figsize=(5, 3))
    plt.plot(x_vals, y_vals, label=f'f(x) = {expr}')
    plt.plot(x_vals, dy_vals, label=f"f'(x) = {derivative_expr}", linestyle='--')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True)

    # 그래프 이미지를 메모리에 저장
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img = PILImage.open(buf)

    # 이미지를 base64로 인코딩하여 URL 형식으로 변환
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return f"data:image/png;base64,{img_data}"

if __name__ == "__main__":
    app.run(debug=True)
