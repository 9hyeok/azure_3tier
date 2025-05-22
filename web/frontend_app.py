import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

# Streamlit 중앙 버튼 UI
st.title("☁️ Azure 계정 신청 시스템")

col1, col2, col3 = st.columns(3)
if col1.button("신청"):
    st.session_state["page"] = "신청"
if col2.button("조회"):
    st.session_state["page"] = "조회"
if col3.button("관리자"):
    st.session_state["page"] = "관리자"
st.divider()

if "page" not in st.session_state:
    st.session_state["page"] = "신청"

# 신청
if st.session_state["page"] == "신청":
    st.subheader("📝 사용자 계정 신청")
    name = st.text_input("이름")
    department = st.text_input("소속")
    email = st.text_input("이메일")
    phone = st.text_input("연락처")

    if st.button("신청하기"):
        if name and department and email and phone:
            res = requests.post(f"{API_URL}/request", json={
                "name": name, "department": department,
                "email": email, "phone": phone
            })
            st.success(res.json().get("message"))
        else:
            st.warning("모든 정보를 입력해주세요.")

# 조회
elif st.session_state["page"] == "조회":
    st.subheader("🔍 신청 상태 조회")
    name = st.text_input("이름")
    department = st.text_input("소속")

    if st.button("조회하기"):
        res = requests.get(f"{API_URL}/status", params={"name": name, "department": department})
        if res.status_code == 200:
            st.dataframe(res.json())
        else:
            st.error("조회 결과 없음")

# 관리자
elif st.session_state["page"] == "관리자":
    st.subheader("🛠️ 관리자 기능")
    password = st.text_input("관리자 비밀번호", type="password")
    if password == "admin123":
        res = requests.get(f"{API_URL}/admin")
        data = res.json()
        original_df = pd.DataFrame(res.json())
        edited_df = st.data_editor(original_df, num_rows="dynamic", use_container_width=True)
        
        if st.button("저장하기"):
            st.success("저장되었습니다.")
            deleted_rows = pd.merge(
            original_df,
            edited_df,
            how="outer",
            indicator=True
            ).query('_merge == "left_only"').drop(columns=["_merge"])

            deleted_list = deleted_rows.to_dict(orient="records")
            del_res = requests.post(f"{API_URL}/admin/delete", json = deleted_list)
            if del_res.status_code == 200:
                st.success(del_res.json().get("message"))
            else:
                st.error(del_res.json().get("detail"))
            

    else:
        st.warning("올바른 비밀번호를 입력하세요.")
