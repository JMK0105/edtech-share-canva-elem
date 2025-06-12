import streamlit as st
from PIL import Image
import io

# 페이지 설정
st.set_page_config(page_title="이미지 리사이징 챗봇", layout="centered")
st.title("🖼️ 이미지 리사이징 챗봇")
st.write("업로드한 이미지를 원하는 용도(배너, 썸네일 등)에 맞춰 자동으로 리사이징해드려요!")

# 사이즈 템플릿 정의
resize_options = {
    "썸네일 (267x215)": (267, 215),
    "배너 (1200x400)": (1200, 400),
    "인스타 피드 (1080x1080)": (1080, 1080),
    "유튜브 썸네일 (1280x720)": (1280, 720),
    "블로그 본문 (800x600)": (800, 600)
}

# 파일 업로드
uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="원본 이미지", use_column_width=True)

    # 옵션 선택
    selected_option = st.selectbox("용도를 선택해주세요", list(resize_options.keys()))
    target_size = resize_options[selected_option]

    # 비율 유지 여부
    keep_ratio = st.checkbox("비율 유지 (여백 채움)", value=True)

    # 리사이징
    if st.button("리사이징 하기"):
        if keep_ratio:
            resized_img = Image.new("RGB", target_size, (255, 255, 255))
            img_ratio = image.width / image.height
            target_ratio = target_size[0] / target_size[1]

            if img_ratio > target_ratio:
                new_width = target_size[0]
                new_height = int(new_width / img_ratio)
            else:
                new_height = target_size[1]
                new_width = int(new_height * img_ratio)

            resized_original = image.resize((new_width, new_height))
            paste_x = (target_size[0] - new_width) // 2
            paste_y = (target_size[1] - new_height) // 2
            resized_img.paste(resized_original, (paste_x, paste_y))
        else:
            resized_img = image.resize(target_size)

        st.image(resized_img, caption="리사이징된 이미지", use_column_width=True)

        # 이미지 다운로드 처리
        buf = io.BytesIO()
        resized_img.save(buf, format="JPEG")
        byte_im = buf.getvalue()

        st.download_button(
            label="📥 이미지 다운로드",
            data=byte_im,
            file_name=f"resized_{selected_option.replace(' ', '_')}.jpg",
            mime="image/jpeg"
        )
