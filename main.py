import streamlit as st
from PIL import Image, ImageSequence
import io
import openai
import base64

# OpenAI API 키 입력 (환경 변수나 secrets.toml로 관리 권장)
openai.api_key = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else "YOUR_OPENAI_API_KEY"

st.set_page_config(page_title="이미지 리사이징 & AI 확장 챗봇", layout="centered")
st.title("🖼️ 이미지 리사이징 & 확장 챗봇")
st.write("업로드한 이미지를 원하는 용도로 리사이징하거나, AI를 통해 배너형 이미지로 재생성해보세요!")

resize_options = {
    "썸네일 (300x300)": (300, 300),
    "배너 (1200x400)": (1200, 400),
    "인스타 피드 (1080x1080)": (1080, 1080),
    "유튜브 썸네일 (1280x720)": (1280, 720),
    "블로그 본문 (800x600)": (800, 600)
}

uploaded_file = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png", "gif"])

if uploaded_file:
    image = Image.open(uploaded_file)
    is_gif = image.format == "GIF"

    st.image(image, caption="원본 이미지", use_container_width=True)

    selected_option = st.selectbox("용도를 선택해주세요", list(resize_options.keys()) + ["AI 배너 생성 (스타일 유지)"])
    keep_ratio = st.checkbox("비율 유지 (여백 채움)", value=True)

    if selected_option != "AI 배너 생성 (스타일 유지)":
        target_size = resize_options[selected_option]
        if st.button("리사이징 하기"):
            if is_gif:
                frames = []
                for frame in ImageSequence.Iterator(image):
                    frame = frame.convert("RGBA")
                    if keep_ratio:
                        new_frame = Image.new("RGBA", target_size, (255, 255, 255, 0))
                        img_ratio = frame.width / frame.height
                        target_ratio = target_size[0] / target_size[1]

                        if img_ratio > target_ratio:
                            new_width = target_size[0]
                            new_height = int(new_width / img_ratio)
                        else:
                            new_height = target_size[1]
                            new_width = int(new_height * img_ratio)

                        resized = frame.resize((new_width, new_height))
                        paste_x = (target_size[0] - new_width) // 2
                        paste_y = (target_size[1] - new_height) // 2
                        new_frame.paste(resized, (paste_x, paste_y), resized)
                        frames.append(new_frame)
                    else:
                        resized = frame.resize(target_size)
                        frames.append(resized)

                buf = io.BytesIO()
                frames[0].save(buf, format='GIF', save_all=True, append_images=frames[1:], loop=0)
                st.image(buf.getvalue(), caption="리사이징된 GIF", use_container_width=True)
                st.download_button("📥 GIF 다운로드", buf.getvalue(), file_name="resized.gif", mime="image/gif")

            else:
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

                st.image(resized_img, caption="리사이징된 이미지", use_container_width=True)

                buf = io.BytesIO()
                resized_img.save(buf, format="JPEG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="📥 이미지 다운로드",
                    data=byte_im,
                    file_name=f"resized_{selected_option.replace(' ', '_')}.jpg",
                    mime="image/jpeg"
                )

    else:
        if is_gif:
            st.warning("GIF 파일은 AI 배너 생성 기능에서 지원되지 않습니다.")
        elif st.button("AI 배너 생성하기 (OpenAI DALL·E)"):
            st.info("이미지 업로드 중... OpenAI API 호출 중입니다.")

            buf = io.BytesIO()
            image.convert("RGB").save(buf, format="PNG")
            base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

            try:
                response = openai.Image.create_variation(
                    image=buf.getvalue(),
                    n=1,
                    size="1024x1024"
                )
                ai_image_url = response["data"][0]["url"]
                st.image(ai_image_url, caption="🎨 AI가 생성한 배너형 이미지 (스타일 유지)")
                st.markdown(f"[이미지 다운로드]({ai_image_url})")
            except Exception as e:
                st.error(f"OpenAI API 호출 오류: {e}")
