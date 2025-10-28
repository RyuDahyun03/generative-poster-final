# generative-poster-final
import streamlit as st
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import hsv_to_rgb

# --- 0. Streamlit Setup and State Initialization ---

st.set_page_config(layout="wide", page_title="Interactive Generative Poster")

# 초기 팔레트 데이터 (CSV 파일 역할을 대체)
DEFAULT_PALETTE = [
    {"name": "sky", "r": 0.4, "g": 0.7, "b": 1.0},
    {"name": "sun", "r": 1.0, "g": 0.8, "b": 0.2},
    {"name": "forest", "r": 0.2, "g": 0.6, "b": 0.3}
]

# 세션 상태 초기화 (영구적인 데이터 저장소)
if 'custom_palette' not in st.session_state:
    st.session_state.custom_palette = DEFAULT_PALETTE.copy()
if 'current_seed' not in st.session_state:
    st.session_state.current_seed = 0

# --- 1. Generative Functions ---

def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15, petals=5):
    """꽃 모양을 포함한 불규칙한 도형(Blob)을 생성합니다."""
    angles = np.linspace(0, 2*math.pi, points, endpoint=False)
    # 꽃잎 공식 적용
    radii = r * (1 + wobble * (np.sin(angles * petals) + 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

def load_custom_palette():
    """세션 상태에서 사용자 정의 팔레트를 RGB 튜플 리스트로 로드합니다."""
    return [(c['r'], c['g'], c['b']) for c in st.session_state.custom_palette]

def make_palette(k=6, mode="pastel", base_h=0.60):
    """선택된 모드에 따라 색상 팔레트를 생성합니다."""
    if mode == "custom":
        # CSV 모드 대신 Custom 모드로 변경 (세션 상태 사용)
        return load_custom_palette()

    cols = []
    for _ in range(k):
        if mode == "pastel":
            h = random.random(); s = random.uniform(0.15,0.35); v = random.uniform(0.9,1.0)
        elif mode == "vivid":
            h = random.random(); s = random.uniform(0.8,1.0); v = random.uniform(0.8,1.0)
        elif mode == "mono":
            h = base_h; s = random.uniform(0.2,0.6); v = random.uniform(0.5,1.0)
        else: # random
            h = random.random(); s = random.uniform(0.3,1.0); v = random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

def draw_poster(n_layers, palette_mode, seed, blob_r, blob_wobble, blob_petals):
    """
    설정된 매개변수를 사용하여 포스터를 그리고 Matplotlib Figure를 반환합니다.
    """
    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.axis('off')
    ax.set_facecolor((0.97, 0.97, 0.97))

    palette = make_palette(6, mode=palette_mode)
    
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        
        # Blob 크기를 기본 반지름 주변에서 변동
        rr = random.uniform(blob_r * 0.5, blob_r * 1.5) 
        
        # 꽃잎 모양의 Blob 생성
        x, y = blob((cx,cy), r=rr, wobble=blob_wobble, petals=blob_petals)
        color = random.choice(palette)
        alpha = random.uniform(0.3, 0.6)

        # 블러 효과 시뮬레이션: 여러 개의 겹치는 도형을 그려 블러 효과를 만듭니다.
        for i in range(5): 
            offset_x = random.uniform(-0.005, 0.005)
            offset_y = random.uniform(-0.005, 0.005)
            # 알파 값을 점차 낮춰 희미하게 만듭니다.
            ax.fill(x + offset_x, y + offset_y, color=color, alpha=alpha / (i + 1), edgecolor='none')

    ax.text(0.05, 0.95, f"Interactive Poster • {palette_mode}",
              transform=ax.transAxes, fontsize=12, weight="bold")
    
    return fig

# --- 2. Palette Editor Functions (Side Bar) ---

def add_new_color(name, r, g, b):
    """새 색상을 세션 상태 팔레트에 추가합니다."""
    st.session_state.custom_palette.append({"name": name, "r": r, "g": g, "b": b})
    st.success(f"색상 '{name}'이 추가되었습니다.")

def delete_existing_color(name):
    """기존 색상을 세션 상태 팔레트에서 삭제합니다."""
    original_len = len(st.session_state.custom_palette)
    # 리스트 컴프리헨션을 사용하여 이름이 일치하지 않는 요소만 남깁니다.
    st.session_state.custom_palette = [c for c in st.session_state.custom_palette if c['name'] != name]
    if len(st.session_state.custom_palette) < original_len:
        st.success(f"색상 '{name}'이 삭제되었습니다.")
    else:
        st.warning(f"색상 '{name}'을(를) 찾을 수 없습니다.")

# --- 3. Streamlit UI Layout ---

st.title("🌺 인터랙티브 생성형 추상 포스터")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("⚙️ 포스터 설정")
    st.caption("아래 슬라이더와 드롭다운을 사용하여 실시간으로 포스터를 변경하세요.")

    # 1. 포스터 레이어 설정
    n_layers = st.slider("레이어 개수 (Layers)", min_value=3, max_value=20, value=8, step=1)
    
    # 2. 색상 팔레트 모드 설정
    palette_mode = st.selectbox(
        "색상 팔레트 모드", 
        options=["pastel", "vivid", "mono", "random", "custom"], # custom이 csv 대체
        index=0
    )
    
    # 3. Blob 모양 설정
    st.subheader("도형 모양 설정")
    blob_r = st.slider("기본 Blob 반지름 (Radius)", min_value=0.05, max_value=0.8, value=0.3, step=0.01)
    blob_wobble = st.slider("Blob 흔들림 정도 (Wobble)", min_value=0.01, max_value=2.0, value=0.15, step=0.01)
    blob_petals = st.slider("Blob 꽃잎 개수 (Petals)", min_value=1, max_value=10, value=5, step=1)
    
    # 4. 시드 설정
    seed = st.number_input("난수 시드 (Seed)", min_value=0, max_value=9999, value=st.session_state.current_seed, step=1)
    if st.button("새 시드 생성"):
        st.session_state.current_seed = random.randint(0, 9999)
        seed = st.session_state.current_seed
        st.rerun()

with col2:
    st.header("🖼️ 생성된 포스터")
    
    # 포스터 생성 및 표시
    fig = draw_poster(n_layers, palette_mode, seed, blob_r, blob_wobble, blob_petals)
    st.pyplot(fig)
    plt.close(fig) # 메모리 해제

# --- 4. Sidebar for Custom Palette Management ---

with st.sidebar:
    st.header("🎨 사용자 정의 팔레트 관리 (Custom Mode)")
    st.caption("Custom 모드 사용 시 아래 색상 목록이 적용됩니다.")

    df_palette = pd.DataFrame(st.session_state.custom_palette)
    st.dataframe(df_palette, use_container_width=True, hide_index=True)
    
    # 새 색상 추가 폼
    with st.form("add_color_form"):
        st.subheader("색상 추가")
        new_name = st.text_input("이름", key="add_name")
        new_r = st.slider("R (Red)", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="add_r")
        new_g = st.slider("G (Green)", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="add_g")
        new_b = st.slider("B (Blue)", min_value=0.0, max_value=1.0, value=0.5, step=0.01, key="add_b")
        submitted = st.form_submit_button("색상 추가하기")
        
        if submitted and new_name:
            add_new_color(new_name, new_r, new_g, new_b)
            st.rerun()

    # 색상 삭제 폼
    with st.form("delete_color_form"):
        st.subheader("색상 삭제")
        names_to_delete = df_palette['name'].tolist()
        # 팔레트에 색상이 하나라도 있어야 삭제 가능
        if names_to_delete:
            delete_name = st.selectbox("삭제할 색상 이름", options=names_to_delete)
            delete_submitted = st.form_submit_button("색상 삭제하기")
            if delete_submitted:
                delete_existing_color(delete_name)
                st.rerun()
        else:
            st.warning("삭제할 사용자 정의 색상이 없습니다.")
